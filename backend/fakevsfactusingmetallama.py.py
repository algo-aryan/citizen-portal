#meta-llama/Llama-3.3-70B-Instruct
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from serpapi import GoogleSearch

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct"
client = InferenceClient(api_key=HF_TOKEN)

def get_google_evidence(claim):
    search_params = {
        "q": claim,
        "api_key": SERPAPI_KEY,
        "num": 5 # Increased for better context
    }
    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()
        evidence_text = ""
        urls = []
        if "organic_results" in results:
            for res in results["organic_results"]:
                evidence_text += f"Title: {res.get('title')}\nSnippet: {res.get('snippet')}\n\n"
                urls.append(res.get('link'))
        return evidence_text, urls
    except Exception:
        return "", []

def fact_check_pipeline(claim):
    # CRITICAL: Tell the LLM what year it is
    current_date = "January 10, 2026"
    
    evidence, found_urls = get_google_evidence(claim)
    
    # Strictly define the system role and constraints
    system_instruction = (
        f"Today is {current_date}. You are a fact-checking engine. "
        "Your goal is to verify claims based ON THE SEARCH EVIDENCE PROVIDED. "
        "Output ONLY a JSON object. No conversational text."
    )
    
    # Grounded User Prompt
    user_prompt = f"""
    CLAIM TO VERIFY: "{claim}"
    
    SEARCH EVIDENCE:
    {evidence if evidence else "No web results found."}
    
    TASK:
    1. If the evidence supports the claim (even partially), mark verdict as "FACT".
    2. If the evidence directly contradicts the claim, mark verdict as "FAKE".
    3. If there is no clear evidence either way, mark as "UNVERIFIED".
    
    RETURN THIS JSON STRUCTURE:
    {{
      "verdict": "FACT/FAKE/UNVERIFIED",
      "reasoning": "1 sentence explanation",
      "type": "political/general/etc",
      "sources": ["URL1", "URL2"]
    }}
    Rule: If FAKE, sources must be ["Not Found As it is Fake"].
    """

    try:
        response = client.chat_completion(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        
        output = response.choices[0].message.content.strip()
        
        # Strip potential markdown backticks
        if output.startswith("```"):
            output = output.strip("`").replace("json", "", 1).strip()
            
        return output

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    user_input = input("Enter the claim: ")
    print(fact_check_pipeline(user_input))