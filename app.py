import os, json, time, random, string, base64
from datetime import datetime
from flask import Flask, request, jsonify, make_response

# 1) Importa tu módulo de lógica:
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))
from generate_emoji_logic import (
    generate_emoji_id,
    authenticate_request,
    enhance_emoji_prompt,
    load_emoji_history,
    save_emoji_history,
    is_emoji_generated,
    call_replicate_api
)

app = Flask(__name__)

# 2) CORS básico
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

# 3) Rutas de Flask
@app.route("/api/generate-emoji", methods=["GET","POST","OPTIONS"])
def generate_emoji():
    # Preflight
    if request.method == "OPTIONS":
        return make_response("", 204)

    # Autenticación
    ok, msg = authenticate_request(request)
    if not ok:
        return jsonify(error="No autorizado", message=msg), 401

    # GET → estadísticas
    if request.method == "GET":
        history = load_emoji_history()
        today = datetime.utcnow().date()
        today_emojis = [
            e for e in history["generated_emojis"]
            if datetime.fromisoformat(
                 e["generated_at"].replace("Z","+00:00")
               ).date() == today
        ]
        return jsonify({
            "success": True,
            "total_emojis": history["total_generated"],
            "emojis_today": len(today_emojis),
            "last_generated": history["last_generated"]
        })

    # POST → generar emoji
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    force  = data.get("force", False)

    if not prompt:
        return jsonify(error='"prompt" requerido'), 400

    history = load_emoji_history()
    if not force and is_emoji_generated(history, prompt):
        existing = next(
            e for e in history["generated_emojis"]
            if e["prompt"].lower().strip() == prompt.lower().strip()
        )
        return jsonify(success=True, already_generated=True, emoji=existing), 200

    enhanced = enhance_emoji_prompt(prompt)
    image_url = call_replicate_api(prompt, enhanced)

    record = {
      "id":           generate_emoji_id(),
      "prompt":       prompt,
      "enhanced_prompt": enhanced,
      "image_url":    image_url,
      "generated_at": datetime.utcnow().isoformat()+"Z",
      "cost_usd":     0.003,
      "generated_by": os.environ.get("API_USERNAME","unknown")
    }

    history["generated_emojis"].append(record)
    history["total_generated"] += 1
    history["last_generated"] = record
    save_emoji_history(history)

    return jsonify(success=True, emoji=record, total_generated=history["total_generated"]), 200

# 4) Si lo ejecutas localmente:
if __name__ == "__main__":
    app.run(debug=True)
