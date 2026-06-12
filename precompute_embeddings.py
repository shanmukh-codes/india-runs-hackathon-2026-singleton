import json
import gzip
import time
import numpy as np
# pyrefly: ignore [missing-import]
import faiss
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
# pyrefly: ignore [missing-import]
import pickle
import argparse

def extract_candidate_text(candidate):
    """Extract and combine relevant text from a candidate for embedding."""
    texts = []
    
    summary = candidate.get("profile", {}).get("summary", "")
    if summary:
        texts.append(summary)
        
    for job in candidate.get("career_history", []):
        desc = job.get("description", "")
        if desc:
            texts.append(desc)
            
    for skill in candidate.get("skills", []):
        name = skill.get("name", "")
        if name:
            texts.append(name)
            
    return " ".join(texts)

def main():
    parser = argparse.ArgumentParser(description="Precompute FAISS Index")
    parser.add_argument("--candidates", type=str, default="candidates.jsonl", help="Input candidates file")
    args = parser.parse_args()

    start_time = time.time()
    
    # 1. Load the model
    print("Loading SentenceTransformer model (this might take a moment to download)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Read candidates
    filepath = args.candidates
    print(f"Reading candidates from {filepath}...")
    
    candidates = []
    texts = []
    
    try:
        with open(filepath, 'rt', encoding='utf-8') as f:
            if filepath.endswith('.json'):
                data = json.load(f)
                for candidate in data:
                    candidates.append({
                        "candidate_id": candidate.get("candidate_id"),
                        "profile": candidate.get("profile", {}),
                        "redrob_signals": candidate.get("redrob_signals", {}),
                        "skills": candidate.get("skills", [])
                    })
                    texts.append(extract_candidate_text(candidate))
            else:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    candidate = json.loads(line)
                    
                    # We only keep the ID and behavioral signals for the metadata store
                    # to save memory.
                    candidates.append({
                        "candidate_id": candidate.get("candidate_id"),
                        "profile": candidate.get("profile", {}),
                        "redrob_signals": candidate.get("redrob_signals", {}),
                        "skills": candidate.get("skills", [])
                    })
                    texts.append(extract_candidate_text(candidate))
                    
                    if len(candidates) % 10000 == 0:
                        print(f"Loaded {len(candidates)} candidates...")
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}. Please make sure you have unzipped the bundle or run this in the correct folder.")
        return

    print(f"Total candidates loaded: {len(candidates)}")
    
    # 3. Generate embeddings (This is the slow part)
    print("Generating embeddings. This will take 15-30 minutes on CPU...")
    # We use batch_size to speed it up. 
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # 4. Build FAISS Index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    # Inner Product (IndexFlatIP) is equivalent to cosine similarity when vectors are normalized
    index = faiss.IndexFlatIP(dimension) 
    index.add(embeddings)
    
    # 5. Save the index and the metadata
    print("Saving index and metadata to disk...")
    faiss.write_index(index, "candidate_index.faiss")
    
    with open("candidate_metadata.pkl", "wb") as f:
        pickle.dump(candidates, f)
        
    elapsed = time.time() - start_time
    print(f"Done! Pre-computation finished in {elapsed/60:.2f} minutes.")
    print("Created 'candidate_index.faiss' and 'candidate_metadata.pkl'.")

if __name__ == "__main__":
    main()
