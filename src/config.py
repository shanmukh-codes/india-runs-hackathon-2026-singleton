import os

# Paths
DATA_FILE = "candidates.jsonl"
OUT_FILE = "submission.csv"

# =============================================================================
# STAGE 1: HEURISTIC FILTER THRESHOLDS (The Trap Door)
# =============================================================================

# Job titles that indicate a candidate is NOT a fit, regardless of skills listed.
# Used to catch keyword stuffers.
DISALLOWED_TITLE_KEYWORDS = {
    "marketing", "hr ", "human resources", "sales", "accountant", 
    "operations", "customer support", "content writer", "graphic designer", 
    "project manager", "mechanical engineer", "civil engineer", 
    "electrical engineer", "business analyst", "finance", "recruiter"
}

# The absolute minimum and maximum years of experience we will even consider
ABSOLUTE_MIN_YOE = 3.0
ABSOLUTE_MAX_YOE = 15.0

# Behavioral minimums
MIN_RESPONSE_RATE = 0.15 # If they respond to <15% of recruiters, they are effectively ghosts

# =============================================================================
# STAGE 2: SCORING WEIGHTS
# =============================================================================

# The "Sweet Spot" experience
IDEAL_YOE_MIN = 5.0
IDEAL_YOE_MAX = 9.0

# High-value production IR / Vector DB skills from the JD
# We look for these in their `skills` array to boost their score.
PRODUCTION_IR_SKILLS = {
    "pinecone", "weaviate", "qdrant", "milvus", "opensearch", 
    "elasticsearch", "faiss", "sentence-transformers", "rag", "llm fine-tuning"
}

# Used to build the TF-IDF vectorizer for semantic matching
# This represents the "vibe" and core requirements of the job
JD_CORE_REQUIREMENTS_TEXT = """
Python embeddings vector databases Pinecone Weaviate Qdrant FAISS retrieval augmented generation RAG.
Production machine learning recommendation systems search hybrid retrieval.
LLM fine-tuning LoRA PEFT sentence-transformers.
Evaluation frameworks NDCG MRR MAP A/B testing learning-to-rank XGBoost.
"""

# =============================================================================
# STAGE 3: BEHAVIORAL MULTIPLIERS
# =============================================================================

# Multipliers applied to the base technical score
MULTIPLIER_NOTICE_PERIOD_UNDER_30 = 1.15
MULTIPLIER_HIGH_GITHUB_ACTIVITY = 1.20   # GitHub score > 50
MULTIPLIER_HIGH_RESPONSE_RATE = 1.15     # Response rate > 0.8
MULTIPLIER_LOCATION_MATCH = 1.20         # Noida/Pune
MULTIPLIER_WILLING_TO_RELOCATE = 1.10
