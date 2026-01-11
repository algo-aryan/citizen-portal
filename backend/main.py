import os
import json
import random  # Added for random source selection
import PIL.Image
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=API_KEY)

# Define the mandatory sources
OFFICIAL_SOURCES = [
    "https://www.eci.gov.in/",
    "https://www.pib.gov.in/"
]

# --- SYSTEM PROMPT FOR CIVIC CHAT ---
# (Kept exactly as provided)
CIVIC_SYSTEM_PROMPT = """
You are BharatMat Assistant, an AI-powered civic awareness assistant designed for a
Voter Awareness & Misinformation Control Platform.

Your responsibilities:
1. Educate voters using factual, verified, publicly available information.
2. Counter misinformation and misleading claims objectively.
3. Explain democratic concepts (elections, Constitution, One Nation One Election)
   in simple, neutral language.
4. Promote informed decision-making without influencing voting choices.
5. Ensure you answer to the point and dont give unecessary information you need to be precise and to the point

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
- Explain what is ONOE if the user asks if asks about benifits and all then tell that also

USER INTERACTION:
- Be respectful and citizen-friendly.
- If asked for opinions or endorsements, politely refuse and redirect to facts.
- If unsure, say “I don’t have enough verified information”.
- TRY TO ANSWER IN SHORT

PRIVACY:
- Do not ask for or store personal or political preference data.

Your goal is to empower voters with knowledge, not influence them.
"""

# --- 1. CIVIC CHAT ENDPOINT ---
# (Kept exactly as provided)
@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json
        user_input = data.get("message", "")
        if not user_input:
            return jsonify({"reply": "Please enter a message."}), 400

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=CIVIC_SYSTEM_PROMPT,
                max_output_tokens=500,
            ),
            contents=user_input
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"reply": "⚠️ System Error: Unable to process chat request."}), 500


# --- 2. FORENSIC LAB ENDPOINT ---
@app.route('/analyze-media', methods=['POST', 'OPTIONS'])
def analyze_media():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        text_claim = request.form.get('text', '')
        image_file = request.files.get('image', None)

        vlm_analysis = "No image provided."
        search_context = "No text claim provided."

        # CASE 1: IMAGE PROCESSING
        if image_file and image_file.filename != '':
            temp_path = "temp_analysis.png"
            image_file.save(temp_path)
            img = PIL.Image.open(temp_path)
            
            vlm_res = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=[img, "Forensic check: Is this AI-generated, a deepfake, or an authentic photo? Look for GAN artifacts."]
            )
            vlm_analysis = vlm_res.text

        # CASE 2: SEARCH/FACT-CHECK
        if text_claim:
            search_tool = types.Tool(google_search=types.GoogleSearch())
            search_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Fact check this claim: {text_claim}. Context from image scan: {vlm_analysis}.",
                config=types.GenerateContentConfig(tools=[search_tool])
            )
            search_context = search_res.text

        # FINAL SYNTHESIS - Removed instructions to find links to save tokens
        final_prompt = f"""
        Evidence: {search_context}
        Visual: {vlm_analysis}
        
        Task: Create a JSON report.
        Return ONLY JSON:
        {{
          "verdict": "FACT/FAKE/UNVERIFIED",
          "reasoning": "2 sentences.",
          "confidence": "HIGH/MEDIUM/LOW",
          "type": "Deepfake/Authentic/Misleading/AI Generated"
        }}
        """
        
        verdict_res = client.models.generate_content(model="gemini-2.0-flash", contents=final_prompt)
        
        raw_text = verdict_res.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            
        # Parse the JSON from LLM
        report = json.loads(raw_text)

        # MANDATORY OVERRIDE: Always pick one of the two URLs randomly
        report["sources"] = random.choice(OFFICIAL_SOURCES)

        return jsonify(report)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "verdict": "ERROR", 
            "reasoning": "System failed to process partial input.", 
            "sources": random.choice(OFFICIAL_SOURCES) # Random source even on error
        }), 500

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)