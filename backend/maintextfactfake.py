import os
import json
import torch
from serpapi import GoogleSearch
from transformers import pipeline

# --- CONFIGURATION ---
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# --- 1. INITIALIZE DeBERTa-v3 ---
print("⏳ Loading DeBERTa-v3 NLI model...")
nli_analyzer = pipeline(
    "text-classification", 
    model="cross-encoder/nli-deberta-v3-small",
    use_fast=False
)

def fetch_serp_evidence(query):
    """Fetches organic search snippets and links from SerpAPI."""
    if not SERPAPI_KEY:
        print("❌ DEBUG: SERPAPI_KEY is missing!")
        return "", []

    params = {
        "q": query,
        "location": "India",
        "hl": "en",
        "gl": "in",
        "google_domain": "google.co.in",
        "api_key": SERPAPI_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        evidence_list = []
        links = []
        
        if "organic_results" in results:
            for res in results["organic_results"][:3]:
                snippet = res.get("snippet", "")
                link = res.get("link", "")
                if snippet:
                    evidence_list.append(snippet)
                    links.append(link)
        
        # DEBUG PRINT FOR INDIVIDUAL QUERY RESULTS
        print(f"   ∟ Found {len(evidence_list)} snippets for this query.")
                    
        return " ".join(evidence_list), links
    except Exception as e:
        print(f"⚠️ DEBUG: Search Error for query '{query}': {e}")
        return "", []

def verify_claim_pipeline(claim):
    print(f"\n{'='*20} DEBUG START {'='*20}")
    print(f"CLAIM: {claim}")
    
    all_snippets = []
    all_urls = []
    
    # Step 1: Query Generation
    queries = [
        f'{claim} site:pib.gov.in',        
        f'{claim} site:eci.gov.in',        
        f'"{claim}"',                      
        f'fact check {claim}'              
    ]
    
    print("\n--- STEP 1: GENERATED QUERIES ---")
    for i, q in enumerate(queries):
        print(f"{i+1}. {q}")

    # Step 2: Retrieval
    print("\n--- STEP 2: FETCHING SOURCES ---")
    for q in queries:
        snippets, links = fetch_serp_evidence(q)
        if snippets:
            all_snippets.append(snippets)
            all_urls.extend(links)

    # Step 3: Check Aggregate Evidence
    full_evidence = " ".join(all_snippets).strip()
    print(f"\n--- STEP 3: EVIDENCE AGGREGATION ---")
    print(f"Total Snippets Gathered: {len(all_snippets)}")
    print(f"Total Unique URLs: {len(set(all_urls))}")
    
    if not full_evidence:
        print("🛑 DEBUG: STOPPING - No evidence found to analyze.")
        return {
            "verdict": "UNVERIFIED",
            "reasoning": "Search returned zero results from official/trusted sources.",
            "sources": "Not Found"
        }

    # Step 4: NLI Verification
    print("\n--- STEP 4: DeBERTa ANALYSIS ---")
    # Truncate evidence if it's too long for DeBERTa (max 512 tokens usually)
    nli_result = nli_analyzer([{"text": full_evidence[:2000], "text_pair": claim}])[0]
    
    label = nli_result['label'].upper()
    score = nli_result['score']
    print(f"Raw NLI Label: {label}")
    print(f"Raw Confidence: {score:.4f}")

    # Step 5: Final Result
    verdict = "UNVERIFIED"
    # Logic: If confidence is too low, we don't commit to FACT or FAKE
    if label == "ENTAILMENT" and score > 0.5:
        verdict = "FACT"
    elif label == "CONTRADICTION" and score > 0.5:
        verdict = "FAKE"
    else:
        print(f"⚠️ DEBUG: Score {score:.2f} too low for threshold 0.5")

    print(f"{'='*20} DEBUG END {'='*20}\n")

    return {
        "verdict": verdict,
        "reasoning": f"DeBERTa {label} match ({score:.1%})",
        "sources": list(set(all_urls))[:3] if all_urls else "Not Found",
        "confidence": "HIGH" if score > 0.8 else "MEDIUM"
    }

if __name__ == "__main__":
    user_input = input("Enter the claim: ")
    report = verify_claim_pipeline(user_input)
    print(json.dumps(report, indent=4))