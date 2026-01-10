import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Environment Variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def safe_save(folder, filename, content):
    """Ensures folder exists and writes content safely."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Saved: {filepath}")

def fact_check_pipeline(claim):
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=API_KEY)
    model_id = "gemini-2.0-flash"
    folder_name = "fact_check_results"

    print(f"\n🧐 Analyzing Claim: '{claim}'")

    # --- STEP 1: GENERATE QUERIES ---
    query_prompt = f"Generate 3-4 search queries to verify this claim: '{claim}'. Return ONLY the queries, one per line."
    q_res = client.models.generate_content(model=model_id, contents=query_prompt)
    synthetic_queries = [q.strip() for q in q_res.text.strip().split('\n') if q.strip()]
    
    # Save Step 1
    safe_save(folder_name, "synthetic_queries.txt", "\n".join(synthetic_queries))

    # --- STEP 2: SEARCH & FETCH ---
    all_urls = []
    evidence_text = ""
    
    for query in synthetic_queries:
        print(f"🔍 Searching: {query}...")
        # Use the updated Google Search tool for 2026
        search_tool = types.Tool(google_search=types.GoogleSearch())
        response = client.models.generate_content(
            model=model_id,
            contents=query,
            config=types.GenerateContentConfig(tools=[search_tool])
        )
        
        # Collect URLs from grounding metadata
        metadata = response.candidates[0].grounding_metadata
        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web:
                    all_urls.append(chunk.web.uri)
        
        evidence_text += f"\nQuery: {query}\nEvidence: {response.text}\n"

    # Save Step 2
    unique_urls = list(set(all_urls))
    safe_save(folder_name, "urls.txt", "\n".join(unique_urls))

    # --- STEP 3: FINAL VERDICT ---
    final_prompt = f"""
    Based on this evidence: {evidence_text}
    Verify the claim: {claim}
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
    and for real it is like election notification ,campaign, political informationm,general ,etc, etc

    return a json with keys verdict reasoning sources
    """
    # TYPE OF FAKE
    #SOURCE: FAKE- NOT FOUND , REAL: GIVE
    
    final_res = client.models.generate_content(model=model_id, contents=final_prompt)
    verdict = final_res.text.strip()
    
    # Save Step 3
    safe_save(folder_name, "ans.txt", verdict)

    # Final Terminal Output
    print("\n" + "="*40)
    print(verdict)
    print("="*40)

if __name__ == "__main__":
    user_input = input("Enter the claim: ")
    fact_check_pipeline(user_input)