from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = "AizasyDgPimgQLbFbLgzVwwdJxKptDHUXuU8t7Y"
MODEL_TO_USE = "gemini-1.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_TO_USE}:generateContent?key={API_KEY}"

# --- FRONTEND (Perplex AI Look with Sidebar) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NihitXFire AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #131314; color: white; font-family: sans-serif; }
        .sidebar { background-color: #1e1f20; }
        .chat-container { max-width: 800px; margin: auto; }
        .user-msg { background: #2b2c2f; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
        .ai-msg { padding: 10px; margin-bottom: 20px; border-left: 3px solid #4285f4; }
    </style>
</head>
<body class="flex h-screen">
    <!-- Sidebar -->
    <div class="sidebar w-64 p-5 flex-shrink-0 hidden md:block">
        <h2 class="text-xl font-bold mb-10">NihitXFire AI</h2>
        <nav class="space-y-4">
            <div class="p-2 hover:bg-gray-700 rounded cursor-pointer">🏠 Home</div>
            <div class="p-2 hover:bg-gray-700 rounded cursor-pointer">🔍 Search</div>
            <div class="p-2 hover:bg-gray-700 rounded cursor-pointer">📚 Library</div>
        </nav>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-grow flex flex-col p-5">
        <div id="chat-window" class="flex-grow overflow-y-auto chat-container p-4">
            <div class="ai-msg">Namaste Nihit! Main aapka Gemini AI hoon. Kaise madad karun?</div>
        </div>
        
        <div class="chat-container w-full p-4">
            <div class="relative">
                <input id="user-input" type="text" class="w-full bg-[#2b2c2f] border-none rounded-xl p-4 pr-20 focus:outline-none" placeholder="Ask anything...">
                <button onclick="sendMessage()" class="absolute right-2 top-2 bg-blue-600 px-4 py-2 rounded-lg font-bold">Send</button>
            </div>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const chatWindow = document.getElementById('chat-window');
            const message = input.value;
            if(!message) return;

            // User Message display
            chatWindow.innerHTML += `<div class="user-msg text-right">${message}</div>`;
            input.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                chatWindow.innerHTML += `<div class="ai-msg">${data.response || data.error}</div>`;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            } catch (err) {
                chatWindow.innerHTML += `<div class="ai-msg text-red-500">Error: Connection failed.</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        response = requests.post(API_URL, json=payload)
        response_data = response.json()

        if "candidates" in response_data:
            bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"response": bot_reply})
        return jsonify({"error": "Gemini API Error"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
