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

# def generate_random_prompt():
#     """Generar prompt aleatorio optimizado para UN SOLO emoji"""
    
#     # Tipos de prompts más específicos para UN SOLO emoji
#     prompt_types = [
#         "simple_emotion",
#         "single_object", 
#         "animal_face",
#         "food_item",
#         "transport",
#         "nature_single"
#     ]
    
#     prompt_type = random.choice(prompt_types)
    
#     if prompt_type == "simple_emotion":
#         emotions = ["happy", "sad", "angry", "surprised", "love", "sleepy", "cool", "shy", "excited", "confused"]
#         return f"{random.choice(emotions)} face"
        
#     elif prompt_type == "single_object":
#         objects = ["heart", "star", "sun", "moon", "cloud", "flower", "apple", "pizza slice", "key", "crown"]
#         colors = ["red", "blue", "yellow", "green", "purple", "orange", "pink", "golden"]
#         return f"{random.choice(colors)} {random.choice(objects)}"
        
#     elif prompt_type == "animal_face":
#         animals = ["cat", "dog", "bear", "rabbit", "fox", "panda", "lion", "tiger", "owl", "frog"]
#         return f"{random.choice(animals)} face"
        
#     elif prompt_type == "food_item":
#         foods = ["pizza slice", "hamburger", "ice cream", "donut", "apple", "banana", "coffee cup", "taco", "cookie"]
#         return random.choice(foods)
        
#     elif prompt_type == "transport":
#         vehicles = ["car", "airplane", "boat", "bicycle", "train", "bus", "rocket"]
#         colors = ["red", "blue", "yellow", "green", "white"]
#         return f"{random.choice(colors)} {random.choice(vehicles)}"
        
#     else:  # nature_single
#         nature = ["tree", "flower", "leaf", "mushroom", "cactus", "rose", "tulip"]
#         colors = ["green", "red", "yellow", "pink", "blue", "purple"]
#         return f"{random.choice(colors)} {random.choice(nature)}"

# def enhance_emoji_prompt(base_prompt):
#     """Prompt ULTRA específico para generar SOLO UN emoji"""
    
#     # Comando principal MEGA específico
#     main_command = f"Generate exactly ONE emoji of {base_prompt}"
    
#     # Especificaciones técnicas
#     tech_specs = "single character, centered composition, white background, 3D cartoon style"
    
#     # Negaciones MÚLTIPLES y agresivas
#     negations = "NOT multiple emojis, NOT a collection, NOT a pattern, NOT many characters, NOT several emojis, NOT a grid, NOT repetition"
    
#     # Estructura específica
#     structure = "round emoji design, isolated single character, one emoji only"
    
#     # PROMPT FINAL MEGA ESPECÍFICO
#     return f"{main_command}, {structure}, {tech_specs}, {negations}, exactly one emoji, solo character, individual emoji face"

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

# api/random.py - Endpoint para generar emojis automotrices únicos para CAUTOS
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

# ------------- Utilidades generales ------------- #

def generate_emoji_id():
    """Generar ID único para el emoji"""
    timestamp = str(int(time.time() * 1000))
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"emoji_{timestamp}_{rand_str}"

def authenticate_request(request):
    """Verificar autenticación básica (cabecera Authorization: Basic ...)"""
    API_USERNAME = os.environ.get('API_USERNAME')
    API_PASSWORD = os.environ.get('API_PASSWORD')

    if not API_USERNAME or not API_PASSWORD:
        return False, "Credenciales no configuradas en el servidor"

    auth_header = (
        request.headers.get('Authorization')
        if hasattr(request, 'headers')
        else request.environ.get('HTTP_AUTHORIZATION')
    )

    if not auth_header:
        return False, "Header de autorización requerido"

    if not auth_header.startswith('Basic '):
        return False, "Formato de autorización inválido"

    try:
        decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
        username, password = decoded.split(':', 1)
    except Exception as e:
        return False, f"Error decodificando credenciales: {e}"

    if username == API_USERNAME and password == API_PASSWORD:
        return True, "Autenticado correctamente"

    return False, "Credenciales inválidas"

# ------------- Historial en /tmp para evitar repeticiones ------------- #

HISTORY_FILE = '/tmp/emoji_history.json'

def load_emoji_history():
    """Cargar historial de emojis generados"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"generated_emojis": [], "total_generated": 0, "last_generated": None}

def save_emoji_history(history):
    """Guardar historial"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

# ------------- Generación de prompts exclusivos CAUTOS ------------- #

CAR_TYPES = [
    "compact car", "sedan", "SUV", "electric car", "taxi style car",
    "convertible", "hatchback", "sports car"
]
CAR_COLORS = [
    "cobalt blue", "midnight black", "pearl white", "sunset orange",
    "lime green", "ruby red", "graphite grey", "taxi yellow"
]

def generate_cautos_prompt():
    """Generar un prompt automotriz único para CAUTOS que no se repita"""
    history = load_emoji_history()
    used_prompts = {e['prompt'] for e in history['generated_emojis']}

    max_attempts = 50
    for _ in range(max_attempts):
        prompt = f"{random.choice(CAR_COLORS)} {random.choice(CAR_TYPES)} with CAUTOS logo"
        if prompt not in used_prompts:
            return prompt

    # Si se agotaron intentos, añadir sufijo único para asegurar no repetición
    return f"{random.choice(CAR_COLORS)} {random.choice(CAR_TYPES)} with CAUTOS logo variant {int(time.time())}"

def enhance_emoji_prompt(base_prompt):
    """
    Crear prompt ULTRA específico para Replicate:
    - Un solo emoji relacionado a CAUTOS (aplicación tipo Uber)
    - Estilo 3D cartoon
    - Fondo blanco
    - Composición centrada
    """
    main_command = f"Generate exactly ONE emoji representing {base_prompt}"
    specs = "single character, centered composition, white background, 3D cartoon style"
    negations = (
        "NOT multiple emojis, NOT pattern, NOT repeated elements, NOT grid, "
        "NOT several emojis, NOT collage"
    )
    structure = "round emoji design, isolated character, automobile theme for ride-hailing"
    return f"{main_command}, {structure}, {specs}, {negations}, solo character"

# ------------- Llamada a la API de Replicate ------------- #

def call_replicate_api(prompt, enhanced_prompt):
    token = os.environ.get('REPLICATE_API_TOKEN')
    if not token:
        raise Exception("REPLICATE_API_TOKEN no configurado")

    payload = {
        "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
        "input": {
            "prompt": enhanced_prompt,
            "aspect_ratio": "1:1",
            "num_outputs": 1,
            "num_inference_steps": 4,
            "output_format": "webp"
        }
    }

    req = urllib.request.Request(
        "https://api.replicate.com/v1/predictions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as r:
        if r.status != 201:
            raise Exception(f"Error iniciando predicción: {r.status}")
        result = json.loads(r.read().decode())

    prediction_id = result["id"]

    for _ in range(30):
        time.sleep(2)
        status_req = urllib.request.Request(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers={"Authorization": f"Token {token}"}
        )
        with urllib.request.urlopen(status_req) as sr:
            data = json.loads(sr.read().decode())

        if data["status"] == "succeeded":
            output = data.get("output", [])
            if output:
                return output[0]
            raise Exception("Salida vacía de Replicate")

        if data["status"] in ("failed", "canceled"):
            raise Exception(f"Generación falló: {data.get('error', 'sin detalle')}")

    raise Exception("Timeout esperando respuesta de Replicate")

# ------------- Handler HTTP ------------- #

class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ----------- GET: un solo emoji ----------- #
    def do_GET(self):
        ok, msg = authenticate_request(self)
        if not ok:
            self._json_response(401, {"error": "No autorizado", "message": msg})
            return

        try:
            base_prompt = generate_cautos_prompt()
            enhanced_prompt = enhance_emoji_prompt(base_prompt)
            image_url = call_replicate_api(base_prompt, enhanced_prompt)

            record = {
                "id": generate_emoji_id(),
                "prompt": base_prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_url": image_url,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "cost_usd": 0.003,
                "generated_by": os.getenv("API_USERNAME", "unknown"),
                "is_random": False
            }

            history = load_emoji_history()
            history["generated_emojis"].append(record)
            history["total_generated"] += 1
            history["last_generated"] = record
            save_emoji_history(history)

            self._json_response(200, {
                "success": True,
                "emoji": record,
                "total_generated": history["total_generated"],
                "message": f'Emoji generado para CAUTOS con prompt: "{base_prompt}"'
            })
        except Exception as e:
            self._json_response(500, {"error": "Error interno del servidor", "message": str(e)})

    # ----------- POST: varios emojis (máx 5) ----------- #
    def do_POST(self):
        ok, msg = authenticate_request(self)
        if not ok:
            self._json_response(401, {"error": "No autorizado", "message": msg})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or "{}")
            count = max(1, min(int(data.get("count", 1)), 5))

            history = load_emoji_history()
            generated = []

            for i in range(count):
                try:
                    bp = generate_cautos_prompt()
                    ep = enhance_emoji_prompt(bp)
                    url = call_replicate_api(bp, ep)

                    rec = {
                        "id": generate_emoji_id(),
                        "prompt": bp,
                        "enhanced_prompt": ep,
                        "image_url": url,
                        "generated_at": datetime.utcnow().isoformat() + "Z",
                        "cost_usd": 0.003,
                        "generated_by": os.getenv("API_USERNAME", "unknown"),
                        "is_random": False,
                        "batch_index": i + 1
                    }

                    generated.append(rec)
                    history["generated_emojis"].append(rec)
                    history["total_generated"] += 1
                    history["last_generated"] = rec
                except Exception as e:
                    print(f"Error generando emoji {i+1}: {e}")

            save_emoji_history(history)

            self._json_response(200, {
                "success": True,
                "emojis": generated,
                "total_generated": len(generated),
                "total_cost_usd": len(generated) * 0.003,
                "message": f"Se generaron {len(generated)} emojis CAUTOS únicos"
            })
        except Exception as e:
            self._json_response(500, {"error": "Error interno del servidor", "message": str(e)})

    # ----------- Helpers ----------- #
    def _json_response(self, status, obj):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())
