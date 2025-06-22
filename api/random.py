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

NEGATIVE_PROMPT = (
    "multiple emojis, collage, mosaic, pattern, tiling, repeating elements, "
    "busy background, bordered frame, text, watermark, signature, gradient, "
    "noise, artifacts, disfigured, cropped, blurry, out of frame"
)


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

# --- PROMPTS ESPECÍFICOS CAUTOS (sustituye únicamente estas dos funciones) ---


def generate_random_prompt():
    """
    Genera una descripción base (color + tipo de vehículo + CAUTOS) 
    asegurando que nunca se repita.
    """
    colors = [
        "cobalt blue", "sunset orange", "lime green", "ruby red",
        "graphite grey", "pearl white", "midnight black", "taxi yellow"
    ]
    vehicles = [
        "compact car", "sedan", "SUV", "electric car", "convertible",
        "hatchback", "sports car", "pickup"
    ]

    hist = load_emoji_history()
    used = {e["prompt"] for e in hist["generated_emojis"]}

    for _ in range(50):
        p = f"{random.choice(colors)} {random.choice(vehicles)} with CAUTOS logo"
        if p not in used:
            return p

    # forzar unicidad si ya existe todo
    return f"{random.choice(colors)} {random.choice(vehicles)} with CAUTOS logo {int(time.time())}"


def enhance_emoji_prompt(base_prompt: str) -> str:
    """
    Devuelve el prompt positivo y el negativo;
    el negativo se envía aparte a Replicate para bloquear decoraciones.
    """
    positive = (
        f"Ultra‐detailed 3D cartoon emoji, single centred character, "
        f"{base_prompt}, ride-hailing automobile theme, "
        "plain pure-white background, smooth soft shadows, high-res, "
        "no outline, no border"
    )
    return positive, NEGATIVE_PROMPT

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
            "prompt": positive,
            "negative_prompt": negative,          #  ⬅️  nuevo
            "aspect_ratio": "1:1",
            "num_outputs": 1,
            "num_inference_steps": 2,            #  ⬇️  menos pasos → menos inventiva
            "guidance_scale": 9,                 #  empuja a seguir el prompt
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
