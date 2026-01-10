import os
import datetime
import PIL.Image
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


INPUT_TEXT = "i saw this viral news on tv about election postponed indefinitely by modi ji ."
INPUT_IMAGE_PATH = "/Users/aryangupta/college2/projects/govt-support/work/image copy.png" # Ensure this file exists in your directory

def get_timestamped_folder():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(script_dir, f"check_{timestamp}")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_file(folder, name, content):
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved: {name}")

def run_multimodal_pipeline(text, img_path):
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=API_KEY)
    model_id = "gemini-2.0-flash"
    out_folder = get_timestamped_folder()

    image_context = ""
    
    # --- STAGE 0: IMAGE DESCRIPTION (VLM Analysis) ---
    if img_path and os.path.exists(img_path):
        print("👁️ Stage 0: Performing VLM Visual Analysis...")
        img = PIL.Image.open(img_path)
        vlm_prompt = """
        Analyze this image with high precision for deepfake or manipulation detection. 
        Describe every detail: lighting consistency, shadows, edge blending, text artifacts, 
        and the specific subject matter. If this is a famous location or person, identify them.
        Provide a forensic-level description to be used for fact-checking.
        """
        vlm_res = client.models.generate_content(model=model_id, contents=[img, vlm_prompt])
        image_context = vlm_res.text
        save_file(out_folder, "image_desc.txt", image_context)
    else:
        print("⏩ No image found, skipping VLM stage.")

    # Combine text and image context for the claim
    full_claim_context = f"Text Claim: {text}\nVisual Context: {image_context}"

    # --- STAGE 1: SYNTHETIC QUERIES ---
    print("🕒 Stage 1: Generating evidence-seeking queries...")
    query_prompt = f"""
    Based on this context:
    {full_claim_context}
    
    Generate 3-4 specific search queries to verify if this is FACT or FAKE. 
    Focus on finding:
    - Official news reports or PIB Fact Checks.
    - Weather or astronomical records (if applicable).
    - Original source of the image.
    Return ONLY the queries, one per line.
    
    """
    q_res = client.models.generate_content(model=model_id, contents=query_prompt)
    queries = [q.strip() for q in q_res.text.strip().split('\n') if q.strip()]
    save_file(out_folder, "synthetic_queries.txt", "\n".join(queries))

    # --- STAGE 2: SEARCH GROUNDING ---
    evidence_corpus = ""
    found_urls = []
    
    for q in queries:
        print(f"🔍 Searching: {q}")
        search_tool = types.Tool(google_search=types.GoogleSearch())
        response = client.models.generate_content(
            model=model_id,
            contents=q,
            config=types.GenerateContentConfig(tools=[search_tool])
        )
        
        # Collect Metadata URLs
        meta = response.candidates[0].grounding_metadata
        if meta.grounding_chunks:
            for chunk in meta.grounding_chunks:
                if chunk.web: found_urls.append(chunk.web.uri)
        
        evidence_corpus += f"\n--- Evidence for {q} ---\n{response.text}\n"

    save_file(out_folder, "urls.txt", "\n".join(list(set(found_urls))))

    # --- STAGE 3: FINAL VERDICT ---
    print("🕒 Stage 3: Synthesizing final answer...")
    final_prompt = f"""
    CLAIM CONTEXT: {full_claim_context}
    COLLECTED EVIDENCE: {evidence_corpus}
    
    Decide if this is FACT or FAKE.
    FINAL ANSWER STRUCTURE:
    VERDICT: [FACT/FAKE/UNVERIFIED]
    REASONING: [Precise 1-2 sentence logic]
    SOURCES: [1-2 official source URLs]
    Return strict json
    
    Final Answer structure:
    VERDICT: [FACT/FAKE/UNVERIFIED]
    REASONING: [Short and precise logic]
    Type:
    SOURCES: [1-2 URLs]
    STRICT JSON
    give source as "Not Found As it is Fake" for fake facts
    and for real give few links for that authentic
    
    type of fake it is like phisisng deepfake etc for fake 
    and for real it is like election notification campaign etc

    return a json with keys verdict reasoning sources
    """
    final_res = client.models.generate_content(model=model_id, contents=final_prompt)
    verdict = final_res.text.strip()
    save_file(out_folder, "ans.txt", verdict)

    # --- TERMINAL OUTPUT ---
    print("\n" + "="*50)
    print("FINAL VERDICT")
    print("="*50)
    print(verdict)
    print("="*50)
    print(f"📂 Results folder: {out_folder}")

if __name__ == "__main__":
    run_multimodal_pipeline(INPUT_TEXT, INPUT_IMAGE_PATH)