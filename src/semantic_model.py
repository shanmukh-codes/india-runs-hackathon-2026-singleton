import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import JD_CORE_REQUIREMENTS_TEXT

class SemanticSearcher:
    def __init__(self, index_path="candidate_index.faiss", meta_path="candidate_metadata.pkl"):
        print("Loading FAISS index...")
        self.index = faiss.read_index(index_path)
        
        print("Loading metadata...")
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
            
        print("Loading SentenceTransformer...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pre-calculate the JD embedding
        jd_embedding = self.model.encode([JD_CORE_REQUIREMENTS_TEXT], convert_to_numpy=True)
        faiss.normalize_L2(jd_embedding)
        self.jd_embedding = jd_embedding
        
    def get_top_candidates(self, top_k=2000):
        """
        Query the FAISS index for the semantically closest candidates to the JD.
        """
        distances, indices = self.index.search(self.jd_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            candidate = self.metadata[idx]
            # dist is the cosine similarity because we used IndexFlatIP and normalized
            candidate["base_semantic_score"] = float(dist) 
            results.append(candidate)
            
        return results
