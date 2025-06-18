# api/stats.py - Endpoint de estadísticas
from http.server import BaseHTTPRequestHandler
import json
import os
import base64
from datetime import datetime

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

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return

    def do_GET(self):
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
                'model_used': 'FLUX Schnell (Vercel API)',
                'cost_per_emoji': 0.003,
                'authenticated_user': os.environ.get('API_USERNAME', 'unknown')
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats_data).encode())
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'Error obteniendo estadísticas',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
            return