import argparse
import pandas as pd
import time
from src.pipeline import run_ranking_pipeline

def main():
    parser = argparse.ArgumentParser(description="Redrob Hackathon Ranker")
    # We still accept --candidates to comply with the Hackathon's requested command format,
    # but internally V2 relies on the precomputed FAISS index.
    parser.add_argument("--candidates", type=str, default="candidates.jsonl", help="Original candidates file (required by hackathon runner)")
    parser.add_argument("--out", type=str, default="submission.csv", help="Output CSV path")
    parser.add_argument("--index", type=str, default="candidate_index.faiss", help="Path to FAISS index")
    parser.add_argument("--meta", type=str, default="candidate_metadata.pkl", help="Path to metadata pkl")
    args = parser.parse_args()
    
    print("Starting ranking pipeline V2 (Dense Vectors + Behavior Multipliers)...")
    start_time = time.time()
    
    try:
        top_candidates = run_ranking_pipeline(
            max_top_n=100,
            index_path=args.index,
            meta_path=args.meta
        )
    except FileNotFoundError:
        print(f"Error: Could not find {args.index} or {args.meta}.")
        print("You must run 'python precompute_embeddings.py' first to generate the index!")
        return
    
    # Export to CSV ensuring exact column order required by the validation spec
    df = pd.DataFrame(top_candidates)
    if not df.empty:
        df = df[["candidate_id", "rank", "score", "reasoning"]]
        df.to_csv(args.out, index=False)
        print(f"Successfully exported top {len(df)} candidates to {args.out}")
    else:
        print("Warning: No candidates passed the filters!")
        
    elapsed = time.time() - start_time
    print(f"Pipeline finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
