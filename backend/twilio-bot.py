import os
import requests
import PIL.Image
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not all([GEMINI_API_KEY, TWILIO_SID, TWILIO_TOKEN]):
    print("❌ ERROR: Missing environment variables. Check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# EXACT SYSTEM PROMPT
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
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# Store chat sessions in memory
chat_sessions = {}

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    sender = request.values.get('From')
    user_msg = request.values.get('Body', '').strip()
    num_media = int(request.values.get('NumMedia', 0))

    tw_resp = MessagingResponse()
    reply = tw_resp.message()

    if sender not in chat_sessions:
        chat_sessions[sender] = model.start_chat(history=[])
    
    chat = chat_sessions[sender]

    try:
        if num_media > 0:
            # CASE: User sent an Image
            media_url = request.values.get('MediaUrl0')
            
            # FIXED: Using the correct variable names defined in CONFIGURATION
            response = requests.get(media_url, auth=(TWILIO_SID, TWILIO_TOKEN))
            
            if response.status_code == 200:
                img_path = f"temp_{sender.replace(':', '')}.png"
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                
                img = PIL.Image.open(img_path)
                
                # Analyze image + text context
                analysis_prompt = f"Forensic check and fact-check. User Query: {user_msg}"
                ai_response = chat.send_message([analysis_prompt, img])
                reply.body(ai_response.text)
                
                # Cleanup temp file
                if os.path.exists(img_path): os.remove(img_path)
            else:
                reply.body("⚠️ Error: Could not download the image from WhatsApp.")

        else:
            # CASE: Text-only chat
            if not user_msg:
                reply.body("Please send a message or an image to analyze.")
            else:
                ai_response = chat.send_message(user_msg)
                reply.body(ai_response.text)

    except Exception as e:
        print(f"Error: {e}")
        reply.body("⚠️ System Error: Unable to process your request.")

    return str(tw_resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)