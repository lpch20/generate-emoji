# api/generate-emoji.py - API Python con Autenticación
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
    # Obtener credenciales de variables de entorno
    API_USERNAME = os.environ.get('API_USERNAME')
    API_PASSWORD = os.environ.get('API_PASSWORD')
    
    if not API_USERNAME or not API_PASSWORD:
        return False, "Credenciales no configuradas en el servidor"
    
    # Verificar header de autorización
    auth_header = None
    if hasattr(request, 'headers'):
        auth_header = request.headers.get('Authorization')
    elif hasattr(request, 'environ'):
        auth_header = request.environ.get('HTTP_AUTHORIZATION')
    
    if not auth_header:
        return False, "Header de autorización requerido"
    
    try:
        # Verificar formato: "Basic base64(username:password)"
        if not auth_header.startswith('Basic '):
            return False, "Formato de autorización inválido"
        
        # Decodificar credenciales
        encoded_credentials = auth_header[6:]  # Remover "Basic "
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        # Verificar credenciales
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

def handler(request):
    """Handler principal para Vercel con autenticación"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    # ==================== AUTENTICACIÓN ====================
    is_authenticated, auth_message = authenticate_request(request)
    
    if not is_authenticated:
        error_response = {
            'error': 'No autorizado',
            'message': auth_message,
            'hint': 'Usa: Authorization: Basic base64(username:password)'
        }
        return (json.dumps(error_response), 401, headers)
    
    # ==================== LÓGICA PRINCIPAL ====================
    
    if request.method == 'GET':
        # Endpoint de estadísticas
        try:
            history = load_emoji_history()
            today = datetime.utcnow().date()
            today_emojis = [
                emoji for emoji in history['generated_emojis']
                if datetime.fromisoformat(emoji['generated_at'].replace('Z', '+00:00')).date() == today
            ]
            
            stats_data = {
                'success': True,
                'total_emojis': history['total_generated'],
                'total_cost_usd': round(history['total_generated'] * 0.003, 4),
                'emojis_today': len(today_emojis),
                'cost_today': round(len(today_emojis) * 0.003, 4),
                'last_generated': history['last_generated'],
                'model_used': 'FLUX Schnell (Python API - Autenticado)',
                'cost_per_emoji': 0.003,
                'authenticated_user': os.environ.get('API_USERNAME', 'unknown')
            }
            
            return (json.dumps(stats_data), 200, headers)
            
        except Exception as e:
            error_response = {
                'error': 'Error obteniendo estadísticas',
                'message': str(e)
            }
            return (json.dumps(error_response), 500, headers)
    
    elif request.method == 'POST':
        # Endpoint de generación de emojis
        try:
            # Obtener datos del request
            if hasattr(request, 'get_json'):
                data = request.get_json() or {}
            else:
                try:
                    data = json.loads(request.data.decode('utf-8')) if request.data else {}
                except:
                    data = {}
            
            prompt = data.get('prompt', '').strip()
            force = data.get('force', False)
            
            if not prompt:
                return (json.dumps({'error': 'El parámetro "prompt" es requerido'}), 400, headers)
            
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
                    response = {
                        'success': True,
                        'already_generated': True,
                        'emoji': existing_emoji,
                        'message': 'Este emoji ya fue generado anteriormente',
                        'total_generated': history['total_generated']
                    }
                    return (json.dumps(response), 200, headers)
            
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
            
            response = {
                'success': True,
                'emoji': emoji_record,
                'total_generated': history['total_generated'],
                'cost_usd': 0.003,
                'is_new': True
            }
            
            return (json.dumps(response), 200, headers)
            
        except Exception as e:
            error_response = {
                'error': 'Error interno del servidor',
                'message': str(e)
            }
            return (json.dumps(error_response), 500, headers)
    
    else:
        return (json.dumps({'error': 'Método no permitido'}), 405, headers)


        # ========== GENERADOR ALEATORIO ==========
if __name__ == '__main__':
    print("🎲 Generador de Emojis Aleatorios")
    print()
    
    # Verificar variables de entorno
    username = os.environ.get('API_USERNAME', 'cautos')
    password = os.environ.get('API_PASSWORD', 'CaUtOs*123!!!')
    token = os.environ.get('REPLICATE_API_TOKEN')
    
    if not token:
        print("❌ Configura REPLICATE_API_TOKEN")
        exit(1)
    
    print(f"🔑 Usuario: {username}")
    
    # GENERADOR DE PROMPTS ALEATORIOS
    import random
    
    # Elementos base
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
    
    # GENERAR PROMPT COMPLETAMENTE ALEATORIO
    def generate_random_prompt():
        # Tipo de emoji aleatorio
        emoji_type = random.choice([
            "animal", "object", "food", "face", "activity", "fantasy", "mixed"
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
            foods = ["pizza", "hamburguesa", "helado", "pastel", "café", "té", "donut", 
                    "taco", "sushi", "ramen", "croissant", "manzana", "banana", "fresa"]
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
            
        else:  # mixed - súper aleatorio
            elements = []
            elements.append(random.choice(colors))
            elements.append(random.choice(animals + objects[:10]))
            elements.append(random.choice(emotions + actions))
            if random.random() < 0.3:
                elements.append(random.choice(styles))
            return " ".join(elements)
    
    # GENERAR EMOJI ALEATORIO
    prompt = generate_random_prompt()
    print(f"🎲 Prompt aleatorio: '{prompt}'")
    print(f"🔄 Generando emoji...")
    print("⏳ Esperando resultado...")
    
    # Crear request mock
    class MockRequest:
        def __init__(self, prompt):
            self.method = 'POST'
            self.data = json.dumps({'prompt': prompt}).encode('utf-8')
            creds = f"{username}:{password}"
            encoded = base64.b64encode(creds.encode()).decode()
            self.headers = {
                'Authorization': f'Basic {encoded}',
                'Content-Type': 'application/json'
            }
    
    # Ejecutar
    try:
        request = MockRequest(prompt)
        response_data, status_code, headers = handler(request)
        result = json.loads(response_data)
        
        if result.get('success'):
            print()
            if result.get('already_generated'):
                print("📋 Este emoji ya existía:")
            else:
                print("🆕 ¡Nuevo emoji generado!")
                print(f"💰 Costo: ${result['cost_usd']}")
            
            print(f"🖼️  URL: {result['emoji']['image_url']}")
            print(f"📊 Total generados: {result['total_generated']}")
            
            # Guardar información
            with open('../ultimo_emoji.txt', 'w') as f:
                f.write(f"Prompt: {prompt}\n")
                f.write(f"URL: {result['emoji']['image_url']}\n")
                f.write(f"Fecha: {result['emoji']['generated_at']}\n")
            
            print("💾 Info guardada en ultimo_emoji.txt")
            print(f"🎨 ¡Disfrutá tu emoji '{prompt}'!")
            
        else:
            print(f"❌ Error: {result.get('error')}")
            print(f"💡 Mensaje: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error ejecutando: {e}")
        import traceback
        traceback.print_exc()