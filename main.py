from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ==============================
# 📁 SERVIR FICHIERS AUDIO
# ==============================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================
# 🏠 HOME
# ==============================
@app.get("/")
def home():
    return {"message": "Serveur OK"}

# ==============================
# 🔹 WEBHOOK VERIFICATION
# ==============================
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN reçu:", token)
    print("TOKEN attendu:", VERIFY_TOKEN)
    print("CHALLENGE:", challenge)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="Verification failed")

# ==============================
# 🔹 RECEPTION MESSAGE
# ==============================
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    print("📩 Message reçu :", data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]

        # 🔊 URL de ton audio
        audio_url = "https://communication-fast-api.onrender.com/static/test-ok.mp3"

        send_audio(sender, audio_url)

    except Exception as e:
        print("⚠️ Erreur :", e)

    return {"status": "ok"}

# ==============================
# 🔊 ENVOI AUDIO WHATSAPP
# ==============================
def send_audio(to, audio_url):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {
            "link": audio_url
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("📤 AUDIO envoyé :", response.status_code)
    print(response.text)