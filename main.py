from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ==============================
# 🔹 HOME ROUTE
# ==============================
@app.get("/")
def home():
    return {"message": "Serveur OK"}

# ==============================
# 🔹 VERIFICATION WEBHOOK (GET)
# ==============================
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook vérifié")
        return int(challenge)

    print("❌ Vérification échouée")
    return {"error": "Verification failed"}

# ==============================
# 🔹 RECEPTION MESSAGE (POST)
# ==============================
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    print("📩 Message reçu :")
    print(data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]

        send_message(sender, "test OK ✅")

    except Exception as e:
        print("⚠️ Erreur :", e)

    return {"status": "ok"}

# ==============================
# 🔹 ENVOI MESSAGE WHATSAPP
# ==============================
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("📤 Réponse envoyée :", response.status_code)
    print(response.text)