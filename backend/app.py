import os
import json
import PIL.Image
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
app = Flask(__name__)

# Wide open CORS for development
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

@app.route('/analyze-media', methods=['POST', 'OPTIONS'])
def analyze_media():
    # Handle CORS Pre-flight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

    try:
        text_claim = request.form.get('text', '')
        image_file = request.files.get('image')

        if not image_file:
            return jsonify({"error": "No image uploaded"}), 400

        temp_path = "temp_analysis.png"
        image_file.save(temp_path)
        img = PIL.Image.open(temp_path)

        # 1. Vision Analysis
        vlm_res = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[img, "Identify deepfake artifacts, lighting inconsistencies, or AI generation signs."]
        )

        # 2. Grounding Search
        search_tool = types.Tool(google_search=types.GoogleSearch())
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Fact check: {text_claim}. Use this image description as context: {vlm_res.text}",
            config=types.GenerateContentConfig(tools=[search_tool])
        )

        # 3. Final JSON formatting
        final_prompt = f"""
        Evidence: {response.text}
        Claim: {text_claim}
        Return ONLY a JSON object with keys: verdict, reasoning, sources, confidence, type.
        Classify confidence as either 'HIGH' or 'MEDIUM' or 'LOW' based on detection certainty strictly
        No markdown formatting.
        """
        verdict_res = client.models.generate_content(model="gemini-2.0-flash", contents=final_prompt)
        
        # Parse text to JSON
        raw_text = verdict_res.text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(raw_text))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"verdict": "ERROR", "reasoning": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)