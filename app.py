from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Nihit, maine tumhara API Key wahi rakha hai jo image_5a4b5b.png mein tha
API_KEY = "AizasyDgPimgQLbFbLgzVwwdJxKptDHUXuU8t7Y"
MODEL_TO_USE = "gemini-1.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_TO_USE}:generateContent?key={API_KEY}"

@app.route('/')
def home():
    return "<h1>Nihit's AI Chatbot is Live!</h1><p>Bhai, server chal raha hai. API calls ab /chat endpoint par jayengi.</p>"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # User ka message browser ya app se lega
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Gemini API ko request bhejna
        payload = {
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }
        
        response = requests.post(API_URL, json=payload)
        response_data = response.json()

        # Response nikalna
        if "candidates" in response_data:
            bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"response": bot_reply})
        else:
            return jsonify({"error": "API Error", "details": response_data}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render ke liye dynamic port zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
