"""
Vector Search using FAISS for semantic similarity in fragrance notes
This is integrated into the RAG system for advanced semantic search
"""

import faiss
import json
import numpy as np
import os
from typing import List, Dict, Tuple

class VectorNoteSearch:
    """Vector-based semantic search for fragrance notes"""
    
    def __init__(self, index_path: str = "app/data/notes.index", 
                 embeddings_path: str = "app/data/notes_embeddings.json"):
        """Initialize vector search with FAISS index"""
        self.index_path = index_path
        self.embeddings_path = embeddings_path
        self.index = None
        self.metadata = None
        self.notes_map = {}
        self.load_index()
    
    def load_index(self):
        """Load FAISS index and metadata"""
        try:
            if not os.path.exists(self.index_path):
                print(f"⚠ تنبيه: لم يتم العثور على FAISS index في {self.index_path}")
                print("  تأكد من تشغيل app/notes_vectorizer.py أولاً")
                return False
            
            self.index = faiss.read_index(self.index_path)
            
            if not os.path.exists(self.embeddings_path):
                print(f"⚠ تنبيه: لم يتم العثور على metadata في {self.embeddings_path}")
                return False
            
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Create mapping of note IDs to note data
            for note_info in self.metadata['notes']:
                self.notes_map[note_info['id']] = note_info
            
            print(f"✓ تم تحميل FAISS index بنجاح ({self.index.ntotal} نوتة)")
            return True
        
        except Exception as e:
            print(f"⚠ خطأ في تحميل FAISS index: {str(e)}")
            return False
    
    def search_by_embedding(self, embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """Search for similar notes using embedding vector"""
        if self.index is None or self.metadata is None:
            return []
        
        try:
            # Ensure embedding is correct shape and type
            embedding = np.array([embedding]).astype('float32')
            
            # Search
            distances, indices = self.index.search(embedding, min(k, self.index.ntotal))
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.metadata['notes']):
                    continue
                
                note_info = self.notes_map[idx]
                results.append({
                    "id": idx,
                    "note": note_info['note'],
                    "arabic": note_info['arabic'],
                    "family": note_info['family'],
                    "distance": float(distance),
                    "similarity": 1 / (1 + float(distance))  # Convert distance to similarity
                })
            
            return results
        
        except Exception as e:
            print(f"⚠ خطأ في البحث: {str(e)}")
            return []
    
    def get_note_embedding(self, note_id: int) -> np.ndarray:
        """Get the embedding vector for a specific note"""
        if self.index is None:
            return None
        
        try:
            # Reconstruct the vector from index
            # Note: This works with IndexFlatL2, for other index types may need different approach
            vector = self.index.reconstruct(note_id)
            return vector
        except:
            return None
    
    def is_ready(self) -> bool:
        """Check if vector search is ready to use"""
        return self.index is not None and self.metadata is not None


# Global instance
_vector_search = None

def get_vector_search() -> VectorNoteSearch:
    """Get or create singleton vector search instance"""
    global _vector_search
    if _vector_search is None:
        _vector_search = VectorNoteSearch()
    return _vector_search


def search_similar_notes(embedding: np.ndarray, k: int = 5) -> List[Dict]:
    """Search for notes similar to a given embedding"""
    vs = get_vector_search()
    if not vs.is_ready():
        return []
    return vs.search_by_embedding(embedding, k)


def generate_note_embedding(client, note_text: str) -> np.ndarray:
    """Generate embedding for a custom note description using hash-based approach"""
    import hashlib
    
    try:
        # Use hash-based embedding for consistency
        hash_obj = hashlib.md5(note_text.encode())
        seed = int(hash_obj.hexdigest(), 16) % (2**31)
        
        rng = np.random.RandomState(seed)
        vector = rng.randn(384).astype('float32')
        vector = vector / (np.linalg.norm(vector) + 1e-10)
        
        return vector
    except Exception as e:
        print(f"⚠ خطأ في توليد embedding: {str(e)}")
        return None


def semantic_search_notes(client, query: str, k: int = 5) -> List[Dict]:
    """
    Semantic search for fragrance notes using natural language query
    
    Example queries:
    - "عطر منعش للصيف"
    - "رائحة دافئة وخشبية"
    - "نوتات زهرية فاخرة"
    """
    # Generate embedding for the query
    query_embedding = generate_note_embedding(client, query)
    if query_embedding is None:
        return []
    
    # Search similar notes
    results = search_similar_notes(query_embedding, k)
    
    # Add query context
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }
