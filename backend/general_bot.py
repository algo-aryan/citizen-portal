import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = Flask(__name__)
CORS(app)  # Crucial for frontend-backend communication

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are BharatMat Assistant, an AI-powered civic awareness assistant designed for a
Voter Awareness & Misinformation Control Platform.

Your responsibilities:
1. Educate voters using factual, verified, publicly available information.
2. Counter misinformation and misleading claims objectively.
3. Explain democratic concepts (elections, Constitution, One Nation One Election)
   in simple, neutral language.
4. Promote informed decision-making without influencing voting choices.
5.Ensure you answer to the point and dont give unecessary information you need to be precise and to the point

STRICT NEUTRALITY RULES:
- Do NOT support or oppose any political party, candidate, or ideology.
- Do NOT persuade users to vote in any specific way.
- Present multiple viewpoints when relevant.
- Clearly separate facts, interpretations, and uncertainty.

MISINFORMATION HANDLING:
- If a claim is provided, classify it as:
  Verified / Misleading / Partially False / False / Unverified.
- Explain reasoning calmly and factually.
- Encourage verification from official sources like:
  Election Commission of India (ECI), PIB, Supreme Court judgments,
  and reputed fact-checking organizations.

ONE NATION ONE ELECTION:
-Explain what is ONOE if the user asks if asks about benifits and all then tell that also

USER INTERACTION:
- Be respectful and citizen-friendly.
- If asked for opinions or endorsements, politely refuse and redirect to facts.
- If unsure, say “I don’t have enough verified information”.
-TRY TO ANSWER IN SHORT

PRIVACY:
- Do not ask for or store personal or political preference data.

Your goal is to empower voters with knowledge, not influence them.
"""

# Initialize Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Highly efficient for chat
    system_instruction=SYSTEM_PROMPT
)
chat = model.start_chat(history=[])

@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json
        user_input = data.get("message", "")
        
        if not user_input:
            return jsonify({"reply": "Please enter a message."}), 400

        response = chat.send_message(user_input)
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "⚠️ System Error: Unable to process request."}), 500

if __name__ == '__main__':
    # Running on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)