import pandas as pd
from src.filters import passes_stage_1
from src.semantic_model import SemanticSearcher
from src.behavioral_scorer import apply_behavioral_multipliers
from src.reasoning import generate_reasoning

def run_ranking_pipeline(max_top_n=100, index_path="candidate_index.faiss", meta_path="candidate_metadata.pkl"):
    """
    Orchestrates the V2 ranking pipeline using Dense Vectors.
    """
    searcher = SemanticSearcher(index_path, meta_path)
    
    # Stage 1: Fast retrieval from FAISS
    # Pull the top 2000 semantically matching candidates
    candidates_to_evaluate = searcher.get_top_candidates(top_k=2000)
    
    scored_candidates = []
    
    for candidate in candidates_to_evaluate:
        # Stage 2: The Trap Door
        # Drop honeypots, keyword stuffers, and unqualified candidates
        if not passes_stage_1(candidate):
            continue
            
        # Stage 3: Behavioral Multipliers
        base_score = candidate["base_semantic_score"]
        final_score = apply_behavioral_multipliers(base_score, candidate)
        
        scored_candidates.append({
            "candidate_id": candidate.get("candidate_id"),
            "base_score": base_score,
            "score": final_score,
            "candidate_obj": candidate
        })
        
    # Sort by candidate_id ascending first (stable sort for tie-breaking)
    scored_candidates.sort(key=lambda x: x["candidate_id"])
    # Then sort by score descending (stable sort maintains the ID order for ties)
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Slice the exact top N requested (100)
    top_n = scored_candidates[:max_top_n]
    
    results = []
    # Add explicit rank (1 to 100) and dynamically generate reasoning
    for idx, item in enumerate(top_n):
        rank = idx + 1
        candidate = item["candidate_obj"]
        
        # Stage 4: Generate dynamic, grounded reasoning
        reasoning = generate_reasoning(candidate, item["base_score"], item["score"])
        
        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank,
            "score": item["score"],
            "reasoning": reasoning
        })
        
    return results
