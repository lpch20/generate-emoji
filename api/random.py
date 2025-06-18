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
    """Generar prompt completamente aleatorio para emojis"""
    
    # Categorías de elementos para combinar
    animals = [
        "gato", "perro", "oso", "conejo", "zorro", "león", "tigre", "elefante", 
        "mono", "panda", "koala", "pingüino", "delfín", "ballena", "pez", "pulpo",
        "mariposa", "abeja", "pájaro", "águila", "búho", "gallina", "pato", "rana",
        "serpiente", "tortuga", "caracol", "murciélago", "ardilla", "hamster"
    ]
    
    objects = [
        "corazón", "estrella", "sol", "luna", "nube", "arcoíris", "fuego", "agua",
        "flor", "árbol", "casa", "coche", "avión", "barco", "bicicleta", "tren",
        "pizza", "hamburguesa", "helado", "pastel", "café", "té", "cerveza", "vino",
        "teléfono", "computadora", "libro", "música", "película", "juego", "pelota",
        "regalo", "globo", "bandera", "corona", "diamante", "llave", "bomba"
    ]
    
    emotions = [
        "feliz", "triste", "enojado", "sorprendido", "enamorado", "cansado", "dormido",
        "loco", "genial", "cool", "tímido", "valiente", "asustado", "relajado", "estresado",
        "emocionado", "aburrido", "confundido", "determinado", "orgulloso", "avergonzado"
    ]
    
    actions = [
        "bailando", "cantando", "corriendo", "saltando", "volando", "nadando", "durmiendo",
        "comiendo", "bebiendo", "jugando", "trabajando", "estudiando", "riendo", "llorando",
        "pensando", "soñando", "meditando", "ejercitándose", "cocinando", "leyendo"
    ]
    
    styles = [
        "ninja", "pirata", "robot", "zombie", "superhéroe", "vikingo", "samurai", "mago",
        "chef", "doctor", "artista", "músico", "deportista", "detective", "astronauta",
        "cowboy", "princesa", "rey", "guerrero", "científico", "hippie", "punk"
    ]
    
    colors = [
        "rojo", "azul", "verde", "amarillo", "rosa", "morado", "naranja", "negro",
        "blanco", "dorado", "plateado", "turquesa", "violeta", "marrón", "gris"
    ]
    
    modifiers = [
        "pequeño", "grande", "gigante", "mini", "súper", "ultra", "mega", "micro",
        "brillante", "oscuro", "transparente", "metálico", "peludo", "suave", "duro"
    ]
    
    foods = [
        "pizza", "hamburguesa", "helado", "pastel", "donut", "taco", "sushi", "ramen", 
        "croissant", "manzana", "banana", "fresa", "sandía", "piña", "uva", "naranja"
    ]
    
    weather = [
        "soleado", "lluvioso", "nevado", "nublado", "tormentoso", "ventoso", "brumoso"
    ]
    
    # Tipo de emoji aleatorio
    emoji_type = random.choice([
        "animal", "object", "food", "face", "activity", "fantasy", "weather", "mixed"
    ])
    
    if emoji_type == "animal":
        animal = random.choice(animals)
        emotion = random.choice(emotions)
        if random.random() < 0.5:
            modifier = random.choice(modifiers)
            return f"{modifier} {animal} {emotion}"
        else:
            action = random.choice(actions)
            return f"{animal} {emotion} {action}"
            
    elif emoji_type == "object":
        obj = random.choice(objects)
        color = random.choice(colors)
        modifier = random.choice(modifiers)
        return f"{color} {modifier} {obj}"
        
    elif emoji_type == "food":
        food = random.choice(foods)
        emotion = random.choice(emotions)
        return f"{food} {emotion}"
        
    elif emoji_type == "face":
        emotion = random.choice(emotions)
        style = random.choice(styles)
        return f"cara {emotion} de {style}"
        
    elif emoji_type == "activity":
        action = random.choice(actions)
        animal = random.choice(animals)
        return f"{animal} {action}"
        
    elif emoji_type == "fantasy":
        style = random.choice(styles)
        animal = random.choice(animals)
        color = random.choice(colors)
        return f"{color} {animal} {style}"
        
    elif emoji_type == "weather":
        weather_type = random.choice(weather)
        obj = random.choice(objects[:10])  # Solo algunos objetos
        return f"{obj} {weather_type}"
        
    else:  # mixed - súper aleatorio
        elements = []
        elements.append(random.choice(colors))
        elements.append(random.choice(animals + objects[:10]))
        elements.append(random.choice(emotions + actions))
        if random.random() < 0.3:
            elements.append(random.choice(styles))
        return " ".join(elements)

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