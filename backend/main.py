import os
import json
import PIL.Image
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Environment Variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (Critical for frontend communication)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=API_KEY)

# --- SYSTEM PROMPT FOR CIVIC CHAT ---
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

# --- HELPER: Extract Grounding Link ---
def extract_grounding_link(response):
    """Deeply parses Gemini response to find the primary source URL."""
    try:
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    return chunk.web.uri
        if metadata and metadata.search_entry_point:
            return "Official Records found (Refer to reasoning)"
    except Exception:
        pass
    return "Not Found"

# --- 1. CIVIC CHAT ENDPOINT ---
@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.json
        user_input = data.get("message", "")
        
        if not user_input:
            return jsonify({"reply": "Please enter a message."}), 400

        # Using the new genai client for chat
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
        # 400 FIX: Use .get() to safely check for optional text/image
        text_claim = request.form.get('text', '').strip()
        image_file = request.files.get('image') # Safely returns None if not present

        vlm_analysis = "Visual analysis skipped (No image)."
        search_context = "Grounding skipped (No text)."
        actual_source_link = "Not Found"

        # CASE 1: IMAGE PROCESSING
        if image_file and image_file.filename != '':
            temp_path = "temp_analysis.png"
            image_file.save(temp_path)
            img = PIL.Image.open(temp_path)
            
            vlm_res = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=[img, "Forensic check: Is this image authentic, or does it show AI artifacts/deepfake signs? Provide a technical summary."]
            )
            vlm_analysis = vlm_res.text

        # CASE 2: SEARCH/FACT-CHECK
        if text_claim:
            search_tool = types.Tool(google_search=types.GoogleSearch())
            search_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Fact check this: {text_claim}. Use these visual forensic results as context: {vlm_analysis}. Find the primary source.",
                config=types.GenerateContentConfig(tools=[search_tool])
            )
            search_context = search_res.text
            # SOURCE FIX: Extract the actual URI from grounding metadata
            actual_source_link = extract_grounding_link(search_res)

        # FINAL SYNTHESIS
        final_prompt = f"""
        Evidence: {search_context}
        Visual: {vlm_analysis}
        Source Link: {actual_source_link}
        
        Instructions: Generate a JSON report. If 'Source Link' is a URL, use it in "sources".
        Return ONLY valid JSON.

        {{
          "verdict": "FACT/FAKE/UNVERIFIED",
          "reasoning": "2 sentences explaining the final conclusion.",
          "sources": "{actual_source_link}",
          "confidence": "HIGH/MEDIUM/LOW",
          "type": "Deepfake/Authentic/Misleading/AI Generated"
        }}
        """
        
        verdict_res = client.models.generate_content(model="gemini-2.0-flash", contents=final_prompt)
        
        # Clean and parse JSON
        raw_text = verdict_res.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
        return jsonify(json.loads(raw_text))

    except Exception as e:
        print(f"Forensic Error: {e}")
        return jsonify({
            "verdict": "ERROR", 
            "reasoning": f"Analysis failed: {str(e)}", 
            "sources": "Not Found"
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