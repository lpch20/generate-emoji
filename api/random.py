# # api/random.py - Endpoint para generar emojis aleatorios
# from http.server import BaseHTTPRequestHandler
# import json
# import os
# import time
# import random
# import string
# import base64
# from datetime import datetime
# import urllib.request
# import urllib.parse

# def generate_emoji_id():
#     """Generar ID único para emoji"""
#     timestamp = str(int(time.time() * 1000))
#     random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
#     return f"emoji_{timestamp}_{random_str}"

# def authenticate_request(request):
#     """Verificar autenticación del request"""
#     API_USERNAME = os.environ.get('API_USERNAME')
#     API_PASSWORD = os.environ.get('API_PASSWORD')
    
#     if not API_USERNAME or not API_PASSWORD:
#         return False, "Credenciales no configuradas en el servidor"
    
#     auth_header = None
#     if hasattr(request, 'headers'):
#         auth_header = request.headers.get('Authorization')
#     elif hasattr(request, 'environ'):
#         auth_header = request.environ.get('HTTP_AUTHORIZATION')
    
#     if not auth_header:
#         return False, "Header de autorización requerido"
    
#     try:
#         if not auth_header.startswith('Basic '):
#             return False, "Formato de autorización inválido"
        
#         encoded_credentials = auth_header[6:]
#         decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
#         username, password = decoded_credentials.split(':', 1)
        
#         if username == API_USERNAME and password == API_PASSWORD:
#             return True, "Autenticado correctamente"
#         else:
#             return False, "Credenciales inválidas"
            
#     except Exception as e:
#         return False, f"Error en autenticación: {str(e)}"

# # --- PROMPTS ESPECÍFICOS CAUTOS (sustituye únicamente estas dos funciones) ---


# def generate_random_prompt():
#     """
#     Genera una descripción base (color + tipo de vehículo + CAUTOS) 
#     asegurando que nunca se repita.
#     """
#     colors = [
#         "cobalt blue", "sunset orange", "lime green", "ruby red",
#         "graphite grey", "pearl white", "midnight black", "taxi yellow"
#     ]
#     vehicles = [
#         "compact car", "sedan", "SUV", "electric car", "convertible",
#         "hatchback", "sports car", "pickup"
#     ]

#     hist = load_emoji_history()
#     used = {e["prompt"] for e in hist["generated_emojis"]}

#     for _ in range(50):
#         p = f"{random.choice(colors)} {random.choice(vehicles)} with CAUTOS logo"
#         if p not in used:
#             return p

#     # forzar unicidad si ya existe todo
#     return f"{random.choice(colors)} {random.choice(vehicles)} with CAUTOS logo {int(time.time())}"


# def enhance_emoji_prompt(base_prompt: str) -> str:
#     """
#     Prompt ULTRA-específico para forzar 1 (y solo 1) emoji:
#       • Macro shot de un único personaje
#       • Fondo blanco o transparente
#       • Cartoon / 3D, iluminación suave
#       • Prohibido mosaicos, patrones o grupos
#     """
#     return (
#         f"EXTREME CLOSE-UP macro shot of ONE single emoji: {base_prompt}. "
#         "Centered, full frame, no crop, white background, 3D cartoon render, soft shadows, "
#         "high resolution, vibrant colors. "
#         "Do NOT create multiple objects, NO tiled pattern, NO grid, NO collage, "
#         "NO duplicated elements — exactly ONE centred emoji character."
#     )

# def load_emoji_history():
#     """Cargar historial desde archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
        
#         if os.path.exists(history_file):
#             with open(history_file, 'r') as f:
#                 return json.load(f)
#         else:
#             return {
#                 "generated_emojis": [],
#                 "total_generated": 0,
#                 "last_generated": None
#             }
#     except:
#         return {
#             "generated_emojis": [],
#             "total_generated": 0,
#             "last_generated": None
#         }

# def save_emoji_history(history):
#     """Guardar historial en archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
#         with open(history_file, 'w') as f:
#             json.dump(history, f, indent=2)
#     except Exception as e:
#         print(f"Error guardando historial: {e}")

# def call_replicate_api(prompt, enhanced_prompt):
#     """Llamar a Replicate API directamente"""
#     token = os.environ.get('REPLICATE_API_TOKEN')
#     if not token:
#         raise Exception('REPLICATE_API_TOKEN no configurado')
    
#     # Payload para Replicate
#     payload = {
#         "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
#         "input": {
#             "prompt": enhanced_prompt,
#             "aspect_ratio": "1:1",
#             "num_outputs": 1,
#             "num_inference_steps": 4,
#             "output_format": "webp"
#         }
#     }
    
#     # Crear request
#     data = json.dumps(payload).encode('utf-8')
#     req = urllib.request.Request(
#         'https://api.replicate.com/v1/predictions',
#         data=data,
#         headers={
#             'Authorization': f'Token {token}',
#             'Content-Type': 'application/json'
#         },
#         method='POST'
#     )
    
#     # Enviar request inicial
#     with urllib.request.urlopen(req) as response:
#         if response.status != 201:
#             raise Exception(f'Error iniciando predicción: {response.status}')
#         result = json.loads(response.read().decode('utf-8'))
    
#     prediction_id = result['id']
    
#     # Polling para obtener resultado
#     for attempt in range(30):
#         time.sleep(2)
        
#         status_req = urllib.request.Request(
#             f'https://api.replicate.com/v1/predictions/{prediction_id}',
#             headers={'Authorization': f'Token {token}'}
#         )
        
#         with urllib.request.urlopen(status_req) as status_response:
#             status_data = json.loads(status_response.read().decode('utf-8'))
        
#         status = status_data['status']
        
#         if status == 'succeeded':
#             if status_data.get('output') and len(status_data['output']) > 0:
#                 image_url = status_data['output'][0]
#                 if image_url and image_url != '{}':
#                     return image_url
#                 else:
#                     raise Exception('URL de imagen inválida')
#             else:
#                 raise Exception('Sin output en respuesta')
                
#         elif status == 'failed':
#             error_msg = status_data.get('error', 'Error desconocido')
#             raise Exception(f'Generación falló: {error_msg}')
            
#         elif status == 'canceled':
#             raise Exception('Generación cancelada')
    
#     raise Exception('Timeout esperando resultado')

# class handler(BaseHTTPRequestHandler):
#     def do_OPTIONS(self):
#         self.send_response(204)
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#         self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#         self.end_headers()
#         return

#     def do_GET(self):
#         """GET: Generar emoji aleatorio simple"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             # Generar prompt aleatorio
#             random_prompt = generate_random_prompt()
#             enhanced_prompt = enhance_emoji_prompt(random_prompt)
            
#             # Generar emoji
#             image_url = call_replicate_api(random_prompt, enhanced_prompt)
            
#             # Crear registro
#             emoji_record = {
#                 'id': generate_emoji_id(),
#                 'prompt': random_prompt,
#                 'enhanced_prompt': enhanced_prompt,
#                 'image_url': image_url,
#                 'generated_at': datetime.utcnow().isoformat() + 'Z',
#                 'cost_usd': 0.003,
#                 'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                 'is_random': True
#             }
            
#             # Actualizar historial
#             history = load_emoji_history()
#             history['generated_emojis'].append(emoji_record)
#             history['total_generated'] += 1
#             history['last_generated'] = emoji_record
#             save_emoji_history(history)
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': True,
#                 'emoji': emoji_record,
#                 'total_generated': history['total_generated'],
#                 'cost_usd': 0.003,
#                 'is_random': True,
#                 'message': f'Emoji aleatorio generado con prompt: "{random_prompt}"'
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return

#     def do_POST(self):
#         """POST: Generar múltiples emojis aleatorios"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             # Obtener datos del request
#             content_length = int(self.headers.get('Content-Length', 0))
#             post_data = self.rfile.read(content_length)
            
#             try:
#                 data = json.loads(post_data.decode('utf-8')) if post_data else {}
#             except:
#                 data = {}
            
#             # Número de emojis a generar (máximo 5 para evitar abuse)
#             count = min(int(data.get('count', 1)), 5)
            
#             generated_emojis = []
#             history = load_emoji_history()
            
#             for i in range(count):
#                 try:
#                     # Generar prompt aleatorio
#                     random_prompt = generate_random_prompt()
#                     enhanced_prompt = enhance_emoji_prompt(random_prompt)
                    
#                     # Generar emoji
#                     image_url = call_replicate_api(random_prompt, enhanced_prompt)
                    
#                     # Crear registro
#                     emoji_record = {
#                         'id': generate_emoji_id(),
#                         'prompt': random_prompt,
#                         'enhanced_prompt': enhanced_prompt,
#                         'image_url': image_url,
#                         'generated_at': datetime.utcnow().isoformat() + 'Z',
#                         'cost_usd': 0.003,
#                         'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                         'is_random': True,
#                         'batch_index': i + 1
#                     }
                    
#                     generated_emojis.append(emoji_record)
                    
#                     # Actualizar historial
#                     history['generated_emojis'].append(emoji_record)
#                     history['total_generated'] += 1
#                     history['last_generated'] = emoji_record
                    
#                 except Exception as emoji_error:
#                     print(f"Error generando emoji {i+1}: {emoji_error}")
#                     continue
            
#             # Guardar historial
#             save_emoji_history(history)
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': True,
#                 'emojis': generated_emojis,
#                 'total_generated': len(generated_emojis),
#                 'total_cost_usd': len(generated_emojis) * 0.003,
#                 'is_random': True,
#                 'message': f'Se generaron {len(generated_emojis)} emojis aleatorios'
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return

# api/random.py - Endpoint para generar emojis aleatorios de CAUTOS



# from http.server import BaseHTTPRequestHandler
# import json
# import os
# import time
# import random
# import string
# import base64
# from datetime import datetime
# import urllib.request
# import urllib.parse

# def generate_emoji_id():
#     """Generar ID único para emoji"""
#     timestamp = str(int(time.time() * 1000))
#     random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
#     return f"emoji_{timestamp}_{random_str}"

# def authenticate_request(request):
#     """Verificar autenticación del request"""
#     API_USERNAME = os.environ.get('API_USERNAME')
#     API_PASSWORD = os.environ.get('API_PASSWORD')
    
#     if not API_USERNAME or not API_PASSWORD:
#         return False, "Credenciales no configuradas en el servidor"
    
#     auth_header = None
#     if hasattr(request, 'headers'):
#         auth_header = request.headers.get('Authorization')
#     elif hasattr(request, 'environ'):
#         auth_header = request.environ.get('HTTP_AUTHORIZATION')
    
#     if not auth_header:
#         return False, "Header de autorización requerido"
    
#     try:
#         if not auth_header.startswith('Basic '):
#             return False, "Formato de autorización inválido"
        
#         encoded_credentials = auth_header[6:]
#         decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
#         username, password = decoded_credentials.split(':', 1)
        
#         if username == API_USERNAME and password == API_PASSWORD:
#             return True, "Autenticado correctamente"
#         else:
#             return False, "Credenciales inválidas"
            
#     except Exception as e:
#         return False, f"Error en autenticación: {str(e)}"

# def generate_random_prompt():
#     """
#     Genera una descripción específica para emojis de CAUTOS
#     UN SOLO auto con características específicas
#     """
#     # Tipos de autos específicos para CAUTOS
#     car_types = [
#         "compact sedan", "modern hatchback", "urban SUV", "electric vehicle", 
#         "city car", "eco taxi", "ride-share car", "smart car"
#     ]
    
#     # Colores de autos
#     car_colors = [
#         "bright yellow", "clean white", "modern blue", "silver metallic",
#         "electric green", "urban orange", "professional black", "taxi yellow"
#     ]
    
#     # Características específicas de CAUTOS
#     cautos_features = [
#         "with CAUTOS logo on door", "showing ride-share symbol", 
#         "with app interface display", "displaying 5-star rating",
#         "with GPS navigation active", "showing pickup location pin",
#         "with driver thumbs up visible", "displaying arrival time"
#     ]
    
#     hist = load_emoji_history()
#     used = {e["prompt"] for e in hist["generated_emojis"]}
    
#     # Intentar generar prompt único
#     for _ in range(100):
#         car_type = random.choice(car_types)
#         car_color = random.choice(car_colors)
#         feature = random.choice(cautos_features)
        
#         prompt = f"single {car_color} {car_type} {feature}"
        
#         if prompt not in used:
#             return prompt
    
#     # Si todo está usado, forzar unicidad con timestamp
#     timestamp = int(time.time())
#     return f"single {random.choice(car_colors)} {random.choice(car_types)} CAUTOS {timestamp}"

# def enhance_emoji_prompt(base_prompt: str) -> str:
#     """
#     Prompt ULTRA-específico para generar UN SOLO auto emoji
#     con fondo color #82E6CC y máxima calidad
#     """
#     return (
#         f"A single car emoji: {base_prompt}. "
#         "STRICT REQUIREMENTS: "
#         "- ONE car only, no duplicates "
#         "- Solid background color #82E6CC (light mint green) "
#         "- Car centered in frame "
#         "- High resolution 1024x1024 pixels "
#         "- 3D cartoon style with smooth surfaces "
#         "- Professional lighting with soft shadows "
#         "- Vibrant but clean colors "
#         "- Perfect emoji proportions "
#         "- No other objects in the image "
#         "- No patterns, no grids, no repetitions "
#         "- Square format 1:1 aspect ratio "
#         "ABSOLUTELY FORBIDDEN: multiple cars, car collections, parking lots, "
#         "traffic scenes, car groups, repeated elements, tiled layouts, "
#         "complex backgrounds, other vehicles, patterns, grids, collages"
#     )

# def load_emoji_history():
#     """Cargar historial desde archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
        
#         if os.path.exists(history_file):
#             with open(history_file, 'r') as f:
#                 return json.load(f)
#         else:
#             return {
#                 "generated_emojis": [],
#                 "total_generated": 0,
#                 "last_generated": None
#             }
#     except:
#         return {
#             "generated_emojis": [],
#             "total_generated": 0,
#             "last_generated": None
#         }

# def save_emoji_history(history):
#     """Guardar historial en archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
#         with open(history_file, 'w') as f:
#             json.dump(history, f, indent=2)
#     except Exception as e:
#         print(f"Error guardando historial: {e}")

# def call_replicate_api(prompt, enhanced_prompt):
#     """Llamar a Replicate API con configuración que funcione correctamente"""
#     token = os.environ.get('REPLICATE_API_TOKEN')
#     if not token:
#         raise Exception('REPLICATE_API_TOKEN no configurado')
    
#     print(f"Token disponible: {'Sí' if token else 'No'}")
    
#     # Payload simplificado pero efectivo
#     payload = {
#         "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
#         "input": {
#             "prompt": enhanced_prompt,
#             "negative_prompt": "multiple cars, many vehicles, car lot, parking, traffic, car collection, pattern, grid, tiled, repeated, duplicated, mosaic, collage, group of cars, fleet, convoy, multiple objects, busy scene, crowd, scattered, overlapping, complex, realistic photo, low quality, blurry, pixelated, distorted",
#             "aspect_ratio": "1:1",
#             "num_outputs": 1,
#             "num_inference_steps": 4,    # Volviendo a un valor que funciona
#             "output_format": "webp",     # Volviendo a webp que es más compatible
#             "output_quality": 90         # Calidad alta pero realista
#         }
#     }
    
#     print(f"Payload preparado: {json.dumps(payload, indent=2)}")
    
#     # Crear request
#     data = json.dumps(payload).encode('utf-8')
#     req = urllib.request.Request(
#         'https://api.replicate.com/v1/predictions',
#         data=data,
#         headers={
#             'Authorization': f'Token {token}',
#             'Content-Type': 'application/json'
#         },
#         method='POST'
#     )
    
#     print("Enviando request inicial...")
    
#     # Enviar request inicial
#     try:
#         with urllib.request.urlopen(req) as response:
#             if response.status != 201:
#                 error_body = response.read().decode('utf-8')
#                 print(f"Error en request inicial: {response.status} - {error_body}")
#                 raise Exception(f'Error iniciando predicción: {response.status} - {error_body}')
#             result = json.loads(response.read().decode('utf-8'))
#             print(f"Request inicial exitoso: {result.get('id', 'Sin ID')}")
#     except Exception as e:
#         print(f"Error en urllib.request: {str(e)}")
#         raise
    
#     prediction_id = result['id']
#     print(f"ID de predicción: {prediction_id}")
    
#     # Polling para obtener resultado
#     for attempt in range(30):  # Timeout razonable
#         print(f"Intento {attempt + 1}/30 - Verificando estado...")
#         time.sleep(3)
        
#         status_req = urllib.request.Request(
#             f'https://api.replicate.com/v1/predictions/{prediction_id}',
#             headers={'Authorization': f'Token {token}'}
#         )
        
#         try:
#             with urllib.request.urlopen(status_req) as status_response:
#                 status_data = json.loads(status_response.read().decode('utf-8'))
                
#             status = status_data['status']
#             print(f"Estado actual: {status}")
            
#             if status == 'succeeded':
#                 if status_data.get('output') and len(status_data['output']) > 0:
#                     image_url = status_data['output'][0]
#                     if image_url and image_url != '{}':
#                         print(f"¡Éxito! URL: {image_url}")
#                         return image_url
#                     else:
#                         raise Exception('URL de imagen inválida')
#                 else:
#                     raise Exception('Sin output en respuesta')
                    
#             elif status == 'failed':
#                 error_msg = status_data.get('error', 'Error desconocido')
#                 print(f"Generación falló: {error_msg}")
#                 raise Exception(f'Generación falló: {error_msg}')
                
#             elif status == 'canceled':
#                 print("Generación cancelada")
#                 raise Exception('Generación cancelada')
                
#         except Exception as e:
#             print(f"Error en polling intento {attempt + 1}: {str(e)}")
#             if attempt == 29:  # Último intento
#                 raise
#             continue
    
#     raise Exception('Timeout esperando resultado')

# class handler(BaseHTTPRequestHandler):
#     def do_OPTIONS(self):
#         self.send_response(204)
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#         self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#         self.end_headers()
#         return

#     def do_GET(self):
#         """GET: Generar emoji aleatorio simple"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             print("Iniciando generación de emoji único...")
            
#             # Generar prompt aleatorio específico para CAUTOS
#             random_prompt = generate_random_prompt()
#             print(f"Prompt base: {random_prompt}")
            
#             enhanced_prompt = enhance_emoji_prompt(random_prompt)
#             print(f"Prompt mejorado generado, longitud: {len(enhanced_prompt)}")
            
#             # Generar emoji
#             print("Enviando request a Replicate...")
#             image_url = call_replicate_api(random_prompt, enhanced_prompt)
#             print(f"Imagen generada: {image_url}")
            
#             # Crear registro
#             emoji_record = {
#                 'id': generate_emoji_id(),
#                 'prompt': random_prompt,
#                 'enhanced_prompt': enhanced_prompt,
#                 'image_url': image_url,
#                 'generated_at': datetime.utcnow().isoformat() + 'Z',
#                 'cost_usd': 0.003,
#                 'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport'
#             }
            
#             # Actualizar historial
#             history = load_emoji_history()
#             history['generated_emojis'].append(emoji_record)
#             history['total_generated'] += 1
#             history['last_generated'] = emoji_record
#             save_emoji_history(history)
            
#             print("Emoji generado y guardado exitosamente")
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': True,
#                 'emoji': emoji_record,
#                 'total_generated': history['total_generated'],
#                 'cost_usd': 0.003,
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport',
#                 'message': f'Emoji CAUTOS generado: "{random_prompt}"'
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return

#     def do_POST(self):
#         """POST: Generar múltiples emojis aleatorios"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             # Obtener datos del request
#             content_length = int(self.headers.get('Content-Length', 0))
#             post_data = self.rfile.read(content_length)
            
#             try:
#                 data = json.loads(post_data.decode('utf-8')) if post_data else {}
#             except:
#                 data = {}
            
#             # Número de emojis a generar (máximo 3 para evitar saturación)
#             count = min(int(data.get('count', 1)), 3)
            
#             generated_emojis = []
#             history = load_emoji_history()
            
#             errors = []  # Para tracking de errores
            
#             for i in range(count):
#                 try:
#                     print(f"Iniciando generación {i+1} de {count}")
                    
#                     # Generar prompt aleatorio específico para CAUTOS
#                     random_prompt = generate_random_prompt()
#                     print(f"Prompt generado: {random_prompt}")
                    
#                     enhanced_prompt = enhance_emoji_prompt(random_prompt)
#                     print(f"Prompt mejorado: {enhanced_prompt[:100]}...")
                    
#                     # Generar emoji
#                     print("Llamando a Replicate API...")
#                     image_url = call_replicate_api(random_prompt, enhanced_prompt)
#                     print(f"URL generada: {image_url}")
                    
#                     # Crear registro
#                     emoji_record = {
#                         'id': generate_emoji_id(),
#                         'prompt': random_prompt,
#                         'enhanced_prompt': enhanced_prompt,
#                         'image_url': image_url,
#                         'generated_at': datetime.utcnow().isoformat() + 'Z',
#                         'cost_usd': 0.003,
#                         'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                         'is_random': True,
#                         'batch_index': i + 1,
#                         'theme': 'CAUTOS_transport'
#                     }
                    
#                     generated_emojis.append(emoji_record)
                    
#                     # Actualizar historial
#                     history['generated_emojis'].append(emoji_record)
#                     history['total_generated'] += 1
#                     history['last_generated'] = emoji_record
                    
#                     print(f"Emoji {i+1} generado exitosamente")
                    
#                     # Pausa entre generaciones para evitar rate limiting
#                     if i < count - 1:
#                         time.sleep(2)
                    
#                 except Exception as emoji_error:
#                     error_msg = f"Error generando emoji {i+1}: {str(emoji_error)}"
#                     print(error_msg)
#                     errors.append(error_msg)
#                     continue
            
#             # Guardar historial
#             save_emoji_history(history)
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': len(generated_emojis) > 0,
#                 'emojis': generated_emojis,
#                 'total_generated': len(generated_emojis),
#                 'total_cost_usd': len(generated_emojis) * 0.003,
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport',
#                 'message': f'Se generaron {len(generated_emojis)} emojis CAUTOS',
#                 'errors': errors if errors else None  # Incluir errores si los hay
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return


# from http.server import BaseHTTPRequestHandler
# import json
# import os
# import time
# import random
# import string
# import base64
# from datetime import datetime
# import urllib.request
# import urllib.parse

# def generate_emoji_id():
#     """Generar ID único para emoji"""
#     timestamp = str(int(time.time() * 1000))
#     random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
#     return f"emoji_{timestamp}_{random_str}"

# def authenticate_request(request):
#     """Verificar autenticación del request"""
#     API_USERNAME = os.environ.get('API_USERNAME')
#     API_PASSWORD = os.environ.get('API_PASSWORD')
    
#     if not API_USERNAME or not API_PASSWORD:
#         return False, "Credenciales no configuradas en el servidor"
    
#     auth_header = None
#     if hasattr(request, 'headers'):
#         auth_header = request.headers.get('Authorization')
#     elif hasattr(request, 'environ'):
#         auth_header = request.environ.get('HTTP_AUTHORIZATION')
    
#     if not auth_header:
#         return False, "Header de autorización requerido"
    
#     try:
#         if not auth_header.startswith('Basic '):
#             return False, "Formato de autorización inválido"
        
#         encoded_credentials = auth_header[6:]
#         decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
#         username, password = decoded_credentials.split(':', 1)
        
#         if username == API_USERNAME and password == API_PASSWORD:
#             return True, "Autenticado correctamente"
#         else:
#             return False, "Credenciales inválidas"
            
#     except Exception as e:
#         return False, f"Error en autenticación: {str(e)}"

# def generate_random_prompt():
#     """
#     Genera una descripción específica para emojis de CAUTOS
#     UN SOLO auto con características específicas
#     """
#     # Tipos de autos específicos para CAUTOS
#     car_types = [
#         "compact sedan", "modern hatchback", "urban SUV", "electric vehicle", 
#         "city car", "eco taxi", "ride-share car", "smart car", "delivery van",
#         "bike", "scooter", "motorcycle"
#     ]
    
#     # Colores de autos
#     car_colors = [
#         "bright yellow", "clean white", "modern blue", "silver metallic",
#         "electric green", "urban orange", "professional black", "taxi yellow",
#         "red", "purple", "pink"
#     ]
    
#     # Características específicas de CAUTOS (simplificadas para Clay-3D)
#     cautos_features = [
#         "CAUTOS logo", "ride-share symbol", "app interface", "5-star rating",
#         "GPS navigation", "pickup location", "driver avatar", "arrival time",
#         "eco badge", "premium service", "fast delivery", "city transport"
#     ]
    
#     hist = load_emoji_history()
#     used = {e["prompt"] for e in hist["generated_emojis"]}
    
#     # Intentar generar prompt único
#     for _ in range(100):
#         car_type = random.choice(car_types)
#         car_color = random.choice(car_colors)
#         feature = random.choice(cautos_features)
        
#         prompt = f"{car_color} {car_type} with {feature}"
        
#         if prompt not in used:
#             return prompt
    
#     # Si todo está usado, forzar unicidad con timestamp
#     timestamp = int(time.time())
#     return f"{random.choice(car_colors)} {random.choice(car_types)} CAUTOS {timestamp}"

# def get_random_accessory():
#     """Obtener accesorio aleatorio específico para vehículos CAUTOS"""
#     vehicle_accessories = [
#         "GPS antenna", "taxi light", "delivery box", "bike helmet", 
#         "racing stripes", "eco symbol", "5-star badge", "app screen",
#         "driver cap", "safety vest", "cargo rack", "charging port"
#     ]
    
#     # 60% de probabilidad de tener accesorio, 40% sin accesorio
#     if random.random() < 0.6:
#         return random.choice(vehicle_accessories)
#     else:
#         return None

# def enhance_emoji_prompt(base_prompt: str) -> str:
#     """
#     Prompt siguiendo el estilo Clay-3D de Cautos para vehículos
#     """
#     # Obtener accesorio aleatorio específico para vehículos
#     accessory = get_random_accessory()
    
#     # Construir la parte del vehículo
#     vehicle_part = base_prompt
    
#     # Agregar accesorio si existe
#     accessory_part = f" with {accessory}" if accessory else ""
    
#     # Prompt base siguiendo exactamente el formato Cautos Clay-3D
#     cautos_prompt = f"imagine clay 3D emoji avatar, {vehicle_part}{accessory_part}, deep royal-blue gradient background with abstract curve, toy-like proportions, soft studio light 45° top-left, subtle rim light, smooth matte plastic, soft flat shadow, isometric 3/4 view, high-res SVG, no texture, no outline"
    
#     return cautos_prompt

# def load_emoji_history():
#     """Cargar historial desde archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
        
#         if os.path.exists(history_file):
#             with open(history_file, 'r') as f:
#                 return json.load(f)
#         else:
#             return {
#                 "generated_emojis": [],
#                 "total_generated": 0,
#                 "last_generated": None
#             }
#     except:
#         return {
#             "generated_emojis": [],
#             "total_generated": 0,
#             "last_generated": None
#         }

# def save_emoji_history(history):
#     """Guardar historial en archivo temporal"""
#     try:
#         history_file = '/tmp/emoji_history.json'
#         with open(history_file, 'w') as f:
#             json.dump(history, f, indent=2)
#     except Exception as e:
#         print(f"Error guardando historial: {e}")

# def call_replicate_api(prompt, enhanced_prompt):
#     """Llamar a Replicate API con configuración que funcione correctamente"""
#     token = os.environ.get('REPLICATE_API_TOKEN')
#     if not token:
#         raise Exception('REPLICATE_API_TOKEN no configurado')
    
#     print(f"Token disponible: {'Sí' if token else 'No'}")
    
#     # Payload optimizado para Clay-3D
#     payload = {
#         "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
#         "input": {
#             "prompt": enhanced_prompt,
#             "negative_prompt": "multiple vehicles, many cars, car lot, parking, traffic, vehicle collection, pattern, grid, tiled, repeated, duplicated, mosaic, collage, group of vehicles, fleet, convoy, multiple objects, busy scene, crowd, scattered, overlapping, complex, realistic photo, low quality, blurry, pixelated, distorted, black outline, metallic reflection, fabric texture, grunge texture",
#             "aspect_ratio": "1:1",
#             "num_outputs": 1,
#             "num_inference_steps": 4,
#             "output_format": "webp",
#             "output_quality": 90
#         }
#     }
    
#     print(f"Payload preparado: {json.dumps(payload, indent=2)}")
    
#     # Crear request
#     data = json.dumps(payload).encode('utf-8')
#     req = urllib.request.Request(
#         'https://api.replicate.com/v1/predictions',
#         data=data,
#         headers={
#             'Authorization': f'Token {token}',
#             'Content-Type': 'application/json'
#         },
#         method='POST'
#     )
    
#     print("Enviando request inicial...")
    
#     # Enviar request inicial
#     try:
#         with urllib.request.urlopen(req) as response:
#             if response.status != 201:
#                 error_body = response.read().decode('utf-8')
#                 print(f"Error en request inicial: {response.status} - {error_body}")
#                 raise Exception(f'Error iniciando predicción: {response.status} - {error_body}')
#             result = json.loads(response.read().decode('utf-8'))
#             print(f"Request inicial exitoso: {result.get('id', 'Sin ID')}")
#     except Exception as e:
#         print(f"Error en urllib.request: {str(e)}")
#         raise
    
#     prediction_id = result['id']
#     print(f"ID de predicción: {prediction_id}")
    
#     # Polling para obtener resultado
#     for attempt in range(30):
#         print(f"Intento {attempt + 1}/30 - Verificando estado...")
#         time.sleep(3)
        
#         status_req = urllib.request.Request(
#             f'https://api.replicate.com/v1/predictions/{prediction_id}',
#             headers={'Authorization': f'Token {token}'}
#         )
        
#         try:
#             with urllib.request.urlopen(status_req) as status_response:
#                 status_data = json.loads(status_response.read().decode('utf-8'))
                
#             status = status_data['status']
#             print(f"Estado actual: {status}")
            
#             if status == 'succeeded':
#                 if status_data.get('output') and len(status_data['output']) > 0:
#                     image_url = status_data['output'][0]
#                     if image_url and image_url != '{}':
#                         print(f"¡Éxito! URL: {image_url}")
#                         return image_url
#                     else:
#                         raise Exception('URL de imagen inválida')
#                 else:
#                     raise Exception('Sin output en respuesta')
                    
#             elif status == 'failed':
#                 error_msg = status_data.get('error', 'Error desconocido')
#                 print(f"Generación falló: {error_msg}")
#                 raise Exception(f'Generación falló: {error_msg}')
                
#             elif status == 'canceled':
#                 print("Generación cancelada")
#                 raise Exception('Generación cancelada')
                
#         except Exception as e:
#             print(f"Error en polling intento {attempt + 1}: {str(e)}")
#             if attempt == 29:
#                 raise
#             continue
    
#     raise Exception('Timeout esperando resultado')

# class handler(BaseHTTPRequestHandler):
#     def do_OPTIONS(self):
#         self.send_response(204)
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#         self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#         self.end_headers()
#         return

#     def do_GET(self):
#         """GET: Generar emoji aleatorio simple"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             print("Iniciando generación de emoji Clay-3D CAUTOS...")
            
#             # Generar prompt aleatorio específico para CAUTOS
#             random_prompt = generate_random_prompt()
#             print(f"Prompt base: {random_prompt}")
            
#             enhanced_prompt = enhance_emoji_prompt(random_prompt)
#             print(f"Prompt Clay-3D generado, longitud: {len(enhanced_prompt)}")
            
#             # Generar emoji
#             print("Enviando request a Replicate...")
#             image_url = call_replicate_api(random_prompt, enhanced_prompt)
#             print(f"Imagen generada: {image_url}")
            
#             # Crear registro
#             emoji_record = {
#                 'id': generate_emoji_id(),
#                 'prompt': random_prompt,
#                 'enhanced_prompt': enhanced_prompt,
#                 'image_url': image_url,
#                 'generated_at': datetime.utcnow().isoformat() + 'Z',
#                 'cost_usd': 0.003,
#                 'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport',
#                 'style': 'clay-3d-cautos'
#             }
            
#             # Actualizar historial
#             history = load_emoji_history()
#             history['generated_emojis'].append(emoji_record)
#             history['total_generated'] += 1
#             history['last_generated'] = emoji_record
#             save_emoji_history(history)
            
#             print("Emoji Clay-3D CAUTOS generado y guardado exitosamente")
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': True,
#                 'emoji': emoji_record,
#                 'total_generated': history['total_generated'],
#                 'cost_usd': 0.003,
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport',
#                 'style': 'clay-3d-cautos',
#                 'message': f'Emoji Clay-3D CAUTOS generado: "{random_prompt}"'
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return

#     def do_POST(self):
#         """POST: Generar múltiples emojis aleatorios"""
#         # Verificar autenticación
#         is_authenticated, auth_message = authenticate_request(self)
        
#         if not is_authenticated:
#             self.send_response(401)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'No autorizado',
#                 'message': auth_message,
#                 'hint': 'Usa: Authorization: Basic base64(username:password)'
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return
        
#         try:
#             # Obtener datos del request
#             content_length = int(self.headers.get('Content-Length', 0))
#             post_data = self.rfile.read(content_length)
            
#             try:
#                 data = json.loads(post_data.decode('utf-8')) if post_data else {}
#             except:
#                 data = {}
            
#             # Número de emojis a generar (máximo 3 para evitar saturación)
#             count = min(int(data.get('count', 1)), 3)
            
#             generated_emojis = []
#             history = load_emoji_history()
            
#             errors = []
            
#             for i in range(count):
#                 try:
#                     print(f"Iniciando generación Clay-3D {i+1} de {count}")
                    
#                     # Generar prompt aleatorio específico para CAUTOS
#                     random_prompt = generate_random_prompt()
#                     print(f"Prompt generado: {random_prompt}")
                    
#                     enhanced_prompt = enhance_emoji_prompt(random_prompt)
#                     print(f"Prompt Clay-3D: {enhanced_prompt[:100]}...")
                    
#                     # Generar emoji
#                     print("Llamando a Replicate API...")
#                     image_url = call_replicate_api(random_prompt, enhanced_prompt)
#                     print(f"URL generada: {image_url}")
                    
#                     # Crear registro
#                     emoji_record = {
#                         'id': generate_emoji_id(),
#                         'prompt': random_prompt,
#                         'enhanced_prompt': enhanced_prompt,
#                         'image_url': image_url,
#                         'generated_at': datetime.utcnow().isoformat() + 'Z',
#                         'cost_usd': 0.003,
#                         'generated_by': os.environ.get('API_USERNAME', 'unknown'),
#                         'is_random': True,
#                         'batch_index': i + 1,
#                         'theme': 'CAUTOS_transport',
#                         'style': 'clay-3d-cautos'
#                     }
                    
#                     generated_emojis.append(emoji_record)
                    
#                     # Actualizar historial
#                     history['generated_emojis'].append(emoji_record)
#                     history['total_generated'] += 1
#                     history['last_generated'] = emoji_record
                    
#                     print(f"Emoji Clay-3D {i+1} generado exitosamente")
                    
#                     # Pausa entre generaciones para evitar rate limiting
#                     if i < count - 1:
#                         time.sleep(2)
                    
#                 except Exception as emoji_error:
#                     error_msg = f"Error generando emoji {i+1}: {str(emoji_error)}"
#                     print(error_msg)
#                     errors.append(error_msg)
#                     continue
            
#             # Guardar historial
#             save_emoji_history(history)
            
#             self.send_response(200)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             response = {
#                 'success': len(generated_emojis) > 0,
#                 'emojis': generated_emojis,
#                 'total_generated': len(generated_emojis),
#                 'total_cost_usd': len(generated_emojis) * 0.003,
#                 'is_random': True,
#                 'theme': 'CAUTOS_transport',
#                 'style': 'clay-3d-cautos',
#                 'message': f'Se generaron {len(generated_emojis)} emojis Clay-3D CAUTOS',
#                 'errors': errors if errors else None
#             }
            
#             self.wfile.write(json.dumps(response).encode())
#             return
            
#         except Exception as e:
#             self.send_response(500)
#             self.send_header('Content-type', 'application/json')
#             self.send_header('Access-Control-Allow-Origin', '*')
#             self.end_headers()
            
#             error_response = {
#                 'error': 'Error interno del servidor',
#                 'message': str(e)
#             }
#             self.wfile.write(json.dumps(error_response).encode())
#             return



from http.server import BaseHTTPRequestHandler
import json
import os
import time
import random
import string
import base64
from datetime import datetime
import urllib.request
import urllib.parse

def generate_emoji_id():
    """Generar ID único para emoji"""
    timestamp = str(int(time.time() * 1000))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"emoji_{timestamp}_{random_str}"

def authenticate_request(request):
    """Verificar autenticación del request"""
    API_USERNAME = os.environ.get('API_USERNAME')
    API_PASSWORD = os.environ.get('API_PASSWORD')
    
    if not API_USERNAME or not API_PASSWORD:
        return False, "Credenciales no configuradas en el servidor"
    
    auth_header = None
    if hasattr(request, 'headers'):
        auth_header = request.headers.get('Authorization')
    elif hasattr(request, 'environ'):
        auth_header = request.environ.get('HTTP_AUTHORIZATION')
    
    if not auth_header:
        return False, "Header de autorización requerido"
    
    try:
        if not auth_header.startswith('Basic '):
            return False, "Formato de autorización inválido"
        
        encoded_credentials = auth_header[6:]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        if username == API_USERNAME and password == API_PASSWORD:
            return True, "Autenticado correctamente"
        else:
            return False, "Credenciales inválidas"
            
    except Exception as e:
        return False, f"Error en autenticación: {str(e)}"

def generate_random_prompt():
    """
    Genera una descripción específica para emojis de CAUTOS
    UN SOLO auto con características específicas
    """
    # Tipos de autos específicos para CAUTOS
    car_types = [
        "compact sedan", "modern hatchback", "urban SUV", "electric vehicle", 
        "city car", "eco taxi", "ride-share car", "smart car", "delivery van",
        "bike", "scooter", "motorcycle"
    ]
    
    # Colores de autos
    car_colors = [
        "bright yellow", "clean white", "modern blue", "silver metallic",
        "electric green", "urban orange", "professional black", "taxi yellow",
        "red", "purple", "pink"
    ]
    
    # Características específicas de CAUTOS (simplificadas para Clay-3D)
    cautos_features = [
        "CAUTOS logo", "ride-share symbol", "app interface", "5-star rating",
        "GPS navigation", "pickup location", "driver avatar", "arrival time",
        "eco badge", "premium service", "fast delivery", "city transport"
    ]
    
    hist = load_emoji_history()
    used = {e["prompt"] for e in hist["generated_emojis"]}
    
    # Intentar generar prompt único
    for _ in range(100):
        car_type = random.choice(car_types)
        car_color = random.choice(car_colors)
        feature = random.choice(cautos_features)
        
        prompt = f"{car_color} {car_type} with {feature}"
        
        if prompt not in used:
            return prompt
    
    # Si todo está usado, forzar unicidad con timestamp
    timestamp = int(time.time())
    return f"{random.choice(car_colors)} {random.choice(car_types)} CAUTOS {timestamp}"

def get_random_accessory():
    """Obtener accesorio aleatorio específico para vehículos CAUTOS"""
    vehicle_accessories = [
        "GPS antenna", "taxi light", "delivery box", "bike helmet", 
        "racing stripes", "eco symbol", "5-star badge", "app screen",
        "driver cap", "safety vest", "cargo rack", "charging port"
    ]
    
    # 60% de probabilidad de tener accesorio, 40% sin accesorio
    if random.random() < 0.6:
        return random.choice(vehicle_accessories)
    else:
        return None

def enhance_emoji_prompt(base_prompt: str) -> str:
    """
    Prompt siguiendo el estilo Clay-3D de Cautos para vehículos
    """
    # Obtener accesorio aleatorio específico para vehículos
    accessory = get_random_accessory()
    
    # Construir la parte del vehículo
    vehicle_part = base_prompt
    
    # Agregar accesorio si existe
    accessory_part = f" with {accessory}" if accessory else ""
    
    # Prompt base siguiendo exactamente el formato Cautos Clay-3D con FONDO TRANSPARENTE
    cautos_prompt = f"imagine clay 3D emoji avatar, {vehicle_part}{accessory_part}, transparent background, toy-like proportions, soft studio light 45° top-left, subtle rim light, smooth matte plastic, soft flat shadow, isometric 3/4 view, high-res SVG, no texture, no outline"
    
    return cautos_prompt

def load_emoji_history():
    """Cargar historial desde archivo temporal"""
    try:
        history_file = '/tmp/emoji_history.json'
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "generated_emojis": [],
                "total_generated": 0,
                "last_generated": None
            }
    except:
        return {
            "generated_emojis": [],
            "total_generated": 0,
            "last_generated": None
        }

def save_emoji_history(history):
    """Guardar historial en archivo temporal"""
    try:
        history_file = '/tmp/emoji_history.json'
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error guardando historial: {e}")

def call_replicate_api(prompt, enhanced_prompt):
    """Llamar a Replicate API con configuración que funcione correctamente"""
    token = os.environ.get('REPLICATE_API_TOKEN')
    if not token:
        raise Exception('REPLICATE_API_TOKEN no configurado')
    
    print(f"Token disponible: {'Sí' if token else 'No'}")
    
    # Payload optimizado para Clay-3D
    payload = {
        "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
        "input": {
            "prompt": enhanced_prompt,
            "negative_prompt": "multiple vehicles, many cars, car lot, parking, traffic, vehicle collection, pattern, grid, tiled, repeated, duplicated, mosaic, collage, group of vehicles, fleet, convoy, multiple objects, busy scene, crowd, scattered, overlapping, complex, realistic photo, low quality, blurry, pixelated, distorted, black outline, metallic reflection, fabric texture, grunge texture, background, colored background, blue background, gradient background, abstract curves, scenery, environment",
            "aspect_ratio": "1:1",
            "num_outputs": 1,
            "num_inference_steps": 4,
            "output_format": "webp",
            "output_quality": 90
        }
    }
    
    print(f"Payload preparado: {json.dumps(payload, indent=2)}")
    
    # Crear request
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.replicate.com/v1/predictions',
        data=data,
        headers={
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    print("Enviando request inicial...")
    
    # Enviar request inicial
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 201:
                error_body = response.read().decode('utf-8')
                print(f"Error en request inicial: {response.status} - {error_body}")
                raise Exception(f'Error iniciando predicción: {response.status} - {error_body}')
            result = json.loads(response.read().decode('utf-8'))
            print(f"Request inicial exitoso: {result.get('id', 'Sin ID')}")
    except Exception as e:
        print(f"Error en urllib.request: {str(e)}")
        raise
    
    prediction_id = result['id']
    print(f"ID de predicción: {prediction_id}")
    
    # Polling para obtener resultado
    for attempt in range(30):
        print(f"Intento {attempt + 1}/30 - Verificando estado...")
        time.sleep(3)
        
        status_req = urllib.request.Request(
            f'https://api.replicate.com/v1/predictions/{prediction_id}',
            headers={'Authorization': f'Token {token}'}
        )
        
        try:
            with urllib.request.urlopen(status_req) as status_response:
                status_data = json.loads(status_response.read().decode('utf-8'))
                
            status = status_data['status']
            print(f"Estado actual: {status}")
            
            if status == 'succeeded':
                if status_data.get('output') and len(status_data['output']) > 0:
                    image_url = status_data['output'][0]
                    if image_url and image_url != '{}':
                        print(f"¡Éxito! URL: {image_url}")
                        return image_url
                    else:
                        raise Exception('URL de imagen inválida')
                else:
                    raise Exception('Sin output en respuesta')
                    
            elif status == 'failed':
                error_msg = status_data.get('error', 'Error desconocido')
                print(f"Generación falló: {error_msg}")
                raise Exception(f'Generación falló: {error_msg}')
                
            elif status == 'canceled':
                print("Generación cancelada")
                raise Exception('Generación cancelada')
                
        except Exception as e:
            print(f"Error en polling intento {attempt + 1}: {str(e)}")
            if attempt == 29:
                raise
            continue
    
    raise Exception('Timeout esperando resultado')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return

    def do_GET(self):
        """GET: Generar emoji aleatorio simple"""
        # Verificar autenticación
        is_authenticated, auth_message = authenticate_request(self)
        
        if not is_authenticated:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'No autorizado',
                'message': auth_message,
                'hint': 'Usa: Authorization: Basic base64(username:password)'
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
        
        try:
            print("Iniciando generación de emoji Clay-3D CAUTOS...")
            
            # Generar prompt aleatorio específico para CAUTOS
            random_prompt = generate_random_prompt()
            print(f"Prompt base: {random_prompt}")
            
            enhanced_prompt = enhance_emoji_prompt(random_prompt)
            print(f"Prompt Clay-3D generado, longitud: {len(enhanced_prompt)}")
            
            # Generar emoji
            print("Enviando request a Replicate...")
            image_url = call_replicate_api(random_prompt, enhanced_prompt)
            print(f"Imagen generada: {image_url}")
            
            # Crear registro
            emoji_record = {
                'id': generate_emoji_id(),
                'prompt': random_prompt,
                'enhanced_prompt': enhanced_prompt,
                'image_url': image_url,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'cost_usd': 0.003,
                'generated_by': os.environ.get('API_USERNAME', 'unknown'),
                'is_random': True,
                'theme': 'CAUTOS_transport',
                'style': 'clay-3d-cautos'
            }
            
            # Actualizar historial
            history = load_emoji_history()
            history['generated_emojis'].append(emoji_record)
            history['total_generated'] += 1
            history['last_generated'] = emoji_record
            save_emoji_history(history)
            
            print("Emoji Clay-3D CAUTOS generado y guardado exitosamente")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'emoji': emoji_record,
                'total_generated': history['total_generated'],
                'cost_usd': 0.003,
                'is_random': True,
                'theme': 'CAUTOS_transport',
                'style': 'clay-3d-cautos',
                'message': f'Emoji Clay-3D CAUTOS generado: "{random_prompt}"'
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'Error interno del servidor',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
            return

    def do_POST(self):
        """POST: Generar múltiples emojis aleatorios"""
        # Verificar autenticación
        is_authenticated, auth_message = authenticate_request(self)
        
        if not is_authenticated:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'No autorizado',
                'message': auth_message,
                'hint': 'Usa: Authorization: Basic base64(username:password)'
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
        
        try:
            # Obtener datos del request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                data = {}
            
            # Número de emojis a generar (máximo 3 para evitar saturación)
            count = min(int(data.get('count', 1)), 3)
            
            generated_emojis = []
            history = load_emoji_history()
            
            errors = []
            
            for i in range(count):
                try:
                    print(f"Iniciando generación Clay-3D {i+1} de {count}")
                    
                    # Generar prompt aleatorio específico para CAUTOS
                    random_prompt = generate_random_prompt()
                    print(f"Prompt generado: {random_prompt}")
                    
                    enhanced_prompt = enhance_emoji_prompt(random_prompt)
                    print(f"Prompt Clay-3D: {enhanced_prompt[:100]}...")
                    
                    # Generar emoji
                    print("Llamando a Replicate API...")
                    image_url = call_replicate_api(random_prompt, enhanced_prompt)
                    print(f"URL generada: {image_url}")
                    
                    # Crear registro
                    emoji_record = {
                        'id': generate_emoji_id(),
                        'prompt': random_prompt,
                        'enhanced_prompt': enhanced_prompt,
                        'image_url': image_url,
                        'generated_at': datetime.utcnow().isoformat() + 'Z',
                        'cost_usd': 0.003,
                        'generated_by': os.environ.get('API_USERNAME', 'unknown'),
                        'is_random': True,
                        'batch_index': i + 1,
                        'theme': 'CAUTOS_transport',
                        'style': 'clay-3d-cautos'
                    }
                    
                    generated_emojis.append(emoji_record)
                    
                    # Actualizar historial
                    history['generated_emojis'].append(emoji_record)
                    history['total_generated'] += 1
                    history['last_generated'] = emoji_record
                    
                    print(f"Emoji Clay-3D {i+1} generado exitosamente")
                    
                    # Pausa entre generaciones para evitar rate limiting
                    if i < count - 1:
                        time.sleep(2)
                    
                except Exception as emoji_error:
                    error_msg = f"Error generando emoji {i+1}: {str(emoji_error)}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue
            
            # Guardar historial
            save_emoji_history(history)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': len(generated_emojis) > 0,
                'emojis': generated_emojis,
                'total_generated': len(generated_emojis),
                'total_cost_usd': len(generated_emojis) * 0.003,
                'is_random': True,
                'theme': 'CAUTOS_transport',
                'style': 'clay-3d-cautos',
                'message': f'Se generaron {len(generated_emojis)} emojis Clay-3D CAUTOS',
                'errors': errors if errors else None
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'Error interno del servidor',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
