# api/generate.py - Endpoint de generación de emojis
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

def enhance_emoji_prompt(base_prompt):
    """Mejorar prompt para emojis"""
    enhancements = [
        "cute emoji style",
        "simple flat design emoji", 
        "colorful emoji icon",
        "clean emoji design",
        "modern emoji style",
        "kawaii emoji",
        "flat emoji design",
        "simple emoji icon"
    ]
    
    styles = [
        "yellow round face",
        "simple geometric shapes",
        "bright colors", 
        "clean lines",
        "flat design",
        "minimalist style"
    ]
    
    enhancement = random.choice(enhancements)
    style = random.choice(styles)
    
    return f"{enhancement}, {base_prompt}, {style}, emoji art, digital illustration, white background, isolated, 3D rendered"

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

def is_emoji_generated(history, prompt):
    """Verificar si emoji ya fue generado"""
    normalized_prompt = prompt.lower().strip()
    return any(emoji['prompt'].lower().strip() == normalized_prompt 
              for emoji in history['generated_emojis'])

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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return

    def do_POST(self):
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
            
            prompt = data.get('prompt', '').strip()
            force = data.get('force', False)
            
            if not prompt:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {'error': 'El parámetro "prompt" es requerido'}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Cargar historial
            history = load_emoji_history()
            
            # Verificar si ya existe (a menos que force = true)
            if not force and is_emoji_generated(history, prompt):
                existing_emoji = next(
                    (emoji for emoji in history['generated_emojis'] 
                     if emoji['prompt'].lower().strip() == prompt.lower().strip()),
                    None
                )
                
                if existing_emoji:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        'success': True,
                        'already_generated': True,
                        'emoji': existing_emoji,
                        'message': 'Este emoji ya fue generado anteriormente',
                        'total_generated': history['total_generated']
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
            
            # Generar nuevo emoji
            enhanced_prompt = enhance_emoji_prompt(prompt)
            image_url = call_replicate_api(prompt, enhanced_prompt)
            
            # Crear registro
            emoji_record = {
                'id': generate_emoji_id(),
                'prompt': prompt,
                'enhanced_prompt': enhanced_prompt,
                'image_url': image_url,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'cost_usd': 0.003,
                'generated_by': os.environ.get('API_USERNAME', 'unknown')
            }
            
            # Actualizar historial
            history['generated_emojis'].append(emoji_record)
            history['total_generated'] += 1
            history['last_generated'] = emoji_record
            
            # Guardar historial
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
                'is_new': True
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