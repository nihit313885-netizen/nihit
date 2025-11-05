# AI Chat Application (Continuous Chat Mode with Decrementing Token Limit)
# This code uses the Gemini API to engage in a continuous conversation.

import requests
import json
import time

# --- CONFIGURATION ---

# Replace with your actual API Key
API_KEY = "AIzaSyDgpimgQLbFbLgzVwwdJxKptDHUXuU8t7Y"
MODEL_TO_USE = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_TO_USE}:generateContent?key={API_KEY}"


# --- GENERATION SETTINGS ---
# Increasing the limit substantially to allow for full code blocks (30 tokens is too restrictive for code).
INITIAL_MAX_TOKENS = 300
MIN_MAX_TOKENS = 5  # The limit won't go below this minimum.


# --- SYSTEM INSTRUCTION ---
# *** FIX: Changing the prompt to focus on ALL code generation, including HTML ***
SYSTEM_PROMPT = "Act as an expert programmer and web developer. When asked for code (Python, HTML, CSS, JavaScript, etc.), always provide the complete, runnable code inside markdown blocks (```language...) and avoid chatty responses."

# --- FUNCTIONS ---

def generate_ai_response(user_query: str, current_max_tokens: int):
    """
    Sends a text query to the Gemini API and processes the response.
    It uses the current_max_tokens for the response length.
    """
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        
        "generationConfig": { 
            "maxOutputTokens": current_max_tokens
        }
    }

    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(3):
        try:
            print(f"DEBUG: Attempting API call (Attempt {attempt + 1}) with Max Tokens: {current_max_tokens}...")
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=15)
            response.raise_for_status()

            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            # Extract text if available
            if candidate and candidate.get('content') and candidate['content'].get('parts'):
                return candidate['content']['parts'][0]['text']
            
            # Handle successful but minimal responses (like for 'hi')
            finish_reason = candidate.get('finishReason')
            if finish_reason in ['MAX_TOKENS', 'STOP']:
                 parts = candidate.get('content', {}).get('parts', [])
                 if parts and parts[0].get('text'):
                     return parts[0]['text']
                 
                 return "Successfully connected! Try asking a longer question."

            else:
                safety_reason = candidate.get('safetyRatings', 'N/A')
                if safety_reason != 'N/A':
                    return f"API output blocked due to Safety Policy. Reason: {safety_reason}"
                
                return "API returned an unexpected response structure or was blocked. Please try a different query."


        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e}")
            if attempt == 2:
                return f"HTTP Error occurred: {e} (Please check your API key validity and billing status)."
            time.sleep(2 ** attempt)
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error occurred: {e}")
            if attempt == 2:
                return f"Request Error occurred: {e} (Possible network issue or wrong API URL)."
            time.sleep(2 ** attempt)

    return "API call failed after 3 attempts."


# --- MAIN EXECUTION ---

# Initialize the token limit state variable
current_max_tokens = INITIAL_MAX_TOKENS

print("="*50)
print(f"AI Chat Bot Initialized | Model: {MODEL_TO_USE}")
print(f"System Role: {SYSTEM_PROMPT}")
print("Limit will decrease by 1 token after every successful chat.")
print("Type 'bye' or 'exit' to end the chat.")
print("="*50)

while True:
    try:
        # Show current token limit to the user
        print(f"Current Max Tokens: {current_max_tokens}")
        user_input = input("You: ")
        
        if user_input.lower() in ['bye', 'exit']:
            print("\nAI: Goodbye! Have a great day.")
            break

        if not user_input.strip():
            continue

        # Get AI response, passing the current token limit
        ai_response = generate_ai_response(user_input, current_max_tokens)

        # Print AI response
        print(f"AI: {ai_response}\n")

        # --- DECREMENT LOGIC ---
        # Only decrement if the limit is above the minimum and the response was successful (i.e., not an API error message)
        if current_max_tokens > MIN_MAX_TOKENS and not ai_response.startswith("HTTP Error occurred") and not ai_response.startswith("API call failed"):
            current_max_tokens -= 1
        
        elif current_max_tokens <= MIN_MAX_TOKENS:
             print(f"NOTE: Token limit has reached the minimum of {MIN_MAX_TOKENS}. It will not decrease further.")
        # -----------------------

    except KeyboardInterrupt:
        print("\nAI: Chat interrupted. Goodbye!")
        break