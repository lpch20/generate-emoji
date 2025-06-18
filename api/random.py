# api/random.py - Endpoint para generar emojis aleatorios
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
    """Generar prompt aleatorio optimizado para UN SOLO emoji"""
    
    # Tipos de prompts más específicos para UN SOLO emoji
    prompt_types = [
        "simple_emotion",
        "single_object", 
        "animal_face",
        "food_item",
        "transport",
        "nature_single"
    ]
    
    prompt_type = random.choice(prompt_types)
    
    if prompt_type == "simple_emotion":
        emotions = ["happy", "sad", "angry", "surprised", "love", "sleepy", "cool", "shy", "excited", "confused"]
        return f"{random.choice(emotions)} face"
        
    elif prompt_type == "single_object":
        objects = ["heart", "star", "sun", "moon", "cloud", "flower", "apple", "pizza slice", "key", "crown"]
        colors = ["red", "blue", "yellow", "green", "purple", "orange", "pink", "golden"]
        return f"{random.choice(colors)} {random.choice(objects)}"
        
    elif prompt_type == "animal_face":
        animals = ["cat", "dog", "bear", "rabbit", "fox", "panda", "lion", "tiger", "owl", "frog"]
        return f"{random.choice(animals)} face"
        
    elif prompt_type == "food_item":
        foods = ["pizza slice", "hamburger", "ice cream", "donut", "apple", "banana", "coffee cup", "taco", "cookie"]
        return random.choice(foods)
        
    elif prompt_type == "transport":
        vehicles = ["car", "airplane", "boat", "bicycle", "train", "bus", "rocket"]
        colors = ["red", "blue", "yellow", "green", "white"]
        return f"{random.choice(colors)} {random.choice(vehicles)}"
        
    else:  # nature_single
        nature = ["tree", "flower", "leaf", "mushroom", "cactus", "rose", "tulip"]
        colors = ["green", "red", "yellow", "pink", "blue", "purple"]
        return f"{random.choice(colors)} {random.choice(nature)}"

def enhance_emoji_prompt(base_prompt):
    """Prompt ULTRA específico para generar SOLO UN emoji"""
    
    # Comando principal MEGA específico
    main_command = f"Generate exactly ONE emoji of {base_prompt}"
    
    # Especificaciones técnicas
    tech_specs = "single character, centered composition, white background, 3D cartoon style"
    
    # Negaciones MÚLTIPLES y agresivas
    negations = "NOT multiple emojis, NOT a collection, NOT a pattern, NOT many characters, NOT several emojis, NOT a grid, NOT repetition"
    
    # Estructura específica
    structure = "round emoji design, isolated single character, one emoji only"
    
    # PROMPT FINAL MEGA ESPECÍFICO
    return f"{main_command}, {structure}, {tech_specs}, {negations}, exactly one emoji, solo character, individual emoji face"

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
    """Llamar a Replicate API directamente"""
    token = os.environ.get('REPLICATE_API_TOKEN')
    if not token:
        raise Exception('REPLICATE_API_TOKEN no configurado')
    
    # Payload para Replicate
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
    
    # Enviar request inicial
    with urllib.request.urlopen(req) as response:
        if response.status != 201:
            raise Exception(f'Error iniciando predicción: {response.status}')
        result = json.loads(response.read().decode('utf-8'))
    
    prediction_id = result['id']
    
    # Polling para obtener resultado
    for attempt in range(30):
        time.sleep(2)
        
        status_req = urllib.request.Request(
            f'https://api.replicate.com/v1/predictions/{prediction_id}',
            headers={'Authorization': f'Token {token}'}
        )
        
        with urllib.request.urlopen(status_req) as status_response:
            status_data = json.loads(status_response.read().decode('utf-8'))
        
        status = status_data['status']
        
        if status == 'succeeded':
            if status_data.get('output') and len(status_data['output']) > 0:
                image_url = status_data['output'][0]
                if image_url and image_url != '{}':
                    return image_url
                else:
                    raise Exception('URL de imagen inválida')
            else:
                raise Exception('Sin output en respuesta')
                
        elif status == 'failed':
            error_msg = status_data.get('error', 'Error desconocido')
            raise Exception(f'Generación falló: {error_msg}')
            
        elif status == 'canceled':
            raise Exception('Generación cancelada')
    
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
            # Generar prompt aleatorio
            random_prompt = generate_random_prompt()
            enhanced_prompt = enhance_emoji_prompt(random_prompt)
            
            # Generar emoji
            image_url = call_replicate_api(random_prompt, enhanced_prompt)
            
            # Crear registro
            emoji_record = {
                'id': generate_emoji_id(),
                'prompt': random_prompt,
                'enhanced_prompt': enhanced_prompt,
                'image_url': image_url,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'cost_usd': 0.003,
                'generated_by': os.environ.get('API_USERNAME', 'unknown'),
                'is_random': True
            }
            
            # Actualizar historial
            history = load_emoji_history()
            history['generated_emojis'].append(emoji_record)
            history['total_generated'] += 1
            history['last_generated'] = emoji_record
            save_emoji_history(history)
            
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
                'message': f'Emoji aleatorio generado con prompt: "{random_prompt}"'
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
            
            # Número de emojis a generar (máximo 5 para evitar abuse)
            count = min(int(data.get('count', 1)), 5)
            
            generated_emojis = []
            history = load_emoji_history()
            
            for i in range(count):
                try:
                    # Generar prompt aleatorio
                    random_prompt = generate_random_prompt()
                    enhanced_prompt = enhance_emoji_prompt(random_prompt)
                    
                    # Generar emoji
                    image_url = call_replicate_api(random_prompt, enhanced_prompt)
                    
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
                        'batch_index': i + 1
                    }
                    
                    generated_emojis.append(emoji_record)
                    
                    # Actualizar historial
                    history['generated_emojis'].append(emoji_record)
                    history['total_generated'] += 1
                    history['last_generated'] = emoji_record
                    
                except Exception as emoji_error:
                    print(f"Error generando emoji {i+1}: {emoji_error}")
                    continue
            
            # Guardar historial
            save_emoji_history(history)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'emojis': generated_emojis,
                'total_generated': len(generated_emojis),
                'total_cost_usd': len(generated_emojis) * 0.003,
                'is_random': True,
                'message': f'Se generaron {len(generated_emojis)} emojis aleatorios'
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