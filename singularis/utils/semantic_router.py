import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import json
import os
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Semantic Router will fallback to keyword matching.")

class SemanticRouter:
    """
    Routes text queries to intents/labels using semantic embeddings.
    
    If sentence-transformers is available, uses 'all-MiniLM-L6-v2' for 
    high-quality semantic matching.
    
    If not available, falls back to keyword/token overlap matching.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', threshold: float = 0.3):
        self.threshold = threshold
        self.routes: Dict[str, List[str]] = defaultdict(list)
        self.embeddings: Dict[str, np.ndarray] = {}
        self.model = None
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Failed to load embedding model: {e}")
                EMBEDDINGS_AVAILABLE = False
    
    def train(self, text: str, label: str):
        """
        Add an example to the router.
        
        Args:
            text: The example text (e.g., "I am so tired")
            label: The intent label (e.g., "sleep")
        """
        self.routes[label].append(text)
        
        if self.model:
            # Compute and store embedding
            emb = self.model.encode(text)
            # Store as tuple key (label, index) -> embedding
            key = f"{label}_{len(self.routes[label])-1}"
            self.embeddings[key] = emb
            
    def predict(self, query: str) -> List[str]:
        """
        Predict labels for a query.
        
        Returns:
            List of matching labels, sorted by confidence.
        """
        if not self.routes:
            return []
            
        if self.model:
            return self._predict_semantic(query)
        else:
            return self._predict_keyword(query)
            
    def _predict_semantic(self, query: str) -> List[str]:
        query_emb = self.model.encode(query)
        scores = {}
        
        for key, emb in self.embeddings.items():
            label = key.split('_')[0]
            # Cosine similarity
            score = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            
            if score > self.threshold:
                # Keep max score for each label
                if score > scores.get(label, 0):
                    scores[label] = score
                    
        # Sort by score
        sorted_labels = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [label for label, score in sorted_labels]
        
    def _predict_keyword(self, query: str) -> List[str]:
        """Fallback basic keyword matching."""
        query_tokens = set(query.lower().split())
        scores = {}
        
        for label, examples in self.routes.items():
            for ex in examples:
                ex_tokens = set(ex.lower().split())
                overlap = len(query_tokens.intersection(ex_tokens))
                if overlap > 0:
                    score = overlap / len(ex_tokens)
                    if score > scores.get(label, 0):
                        scores[label] = score
                        
        sorted_labels = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [label for label, score in sorted_labels]

    def save(self, path: str):
        """Save routes to JSON."""
        with open(path, 'w') as f:
            json.dump(self.routes, f, indent=2)
            
    def load(self, path: str):
        """Load routes from JSON."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                for label, texts in data.items():
                    for text in texts:
                        self.train(text, label)
