# api/index.py - Endpoint raíz de la API
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'message': 'API de Generación de Emojis',
            'version': '1.0',
            'endpoints': {
                'GET /api/stats': 'Obtener estadísticas (requiere auth)',
                'POST /api/generate': 'Generar emoji (requiere auth)'
            },
            'auth': 'Basic Auth requerida'
        }
        
        self.wfile.write(json.dumps(response).encode())
        return