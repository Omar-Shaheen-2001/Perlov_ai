"""
RAG Phase 3: Retrieval — Fetch relevant fragrance notes based on queries
Integrates FAISS index with knowledge base for efficient note retrieval
"""

import json
import faiss
import numpy as np
import os
import hashlib
from typing import List, Dict, Optional

class NotesRetriever:
    """
    Retrieves relevant fragrance notes based on semantic and keyword queries.
    Uses FAISS index for efficient similarity search.
    """
    
    def __init__(self, 
                 kb_path: str = "notes_kb.json",
                 index_path: str = "app/data/notes.index",
                 embeddings_path: str = "app/data/notes_embeddings.json"):
        """Initialize the retriever with knowledge base and FAISS index"""
        self.kb_path = kb_path
        self.index_path = index_path
        self.embeddings_path = embeddings_path
        
        self.notes_db = []
        self.index = None
        self.metadata = None
        self.notes_map = {}
        
        self.load_resources()
    
    def load_resources(self):
        """Load knowledge base and FAISS index"""
        try:
            # Load knowledge base
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    self.notes_db = json.load(f)
                print(f"✓ تم تحميل قاعدة النوتات: {len(self.notes_db)} نوتة")
            else:
                print(f"⚠ لم يتم العثور على قاعدة النوتات")
                return
            
            # Load FAISS index
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"✓ تم تحميل FAISS index: {self.index.ntotal} متجه")
            else:
                print(f"⚠ لم يتم العثور على FAISS index في {self.index_path}")
                return
            
            # Load embeddings metadata
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                # Create mapping
                for note_info in self.metadata['notes']:
                    self.notes_map[note_info['id']] = note_info
                print(f"✓ تم تحميل بيانات Embeddings")
            else:
                print(f"⚠ لم يتم العثور على بيانات Embeddings")
        
        except Exception as e:
            print(f"⚠ خطأ في تحميل الموارد: {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate consistent hash-based embedding for text"""
        try:
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest(), 16) % (2**31)
            
            rng = np.random.RandomState(seed)
            vector = rng.randn(384).astype('float32')
            vector = vector / (np.linalg.norm(vector) + 1e-10)
            
            return vector
        except Exception as e:
            print(f"⚠ خطأ في توليد embedding: {str(e)}")
            return None
    
    def retrieve_by_similarity(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve notes similar to the query using vector similarity
        
        Args:
            query: Query string (e.g., "عطر منعش للصيف")
            top_k: Number of top results to return
        
        Returns:
            List of relevant notes with similarity scores
        """
        if self.index is None or not self.notes_db:
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Search in FAISS index
            query_vec = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))
            
            # Convert results to note objects with similarity scores
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.notes_db):
                    continue
                
                note = self.notes_db[idx].copy()
                note['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                note['retrieval_method'] = 'semantic'
                results.append(note)
            
            return results
        
        except Exception as e:
            print(f"⚠ خطأ في البحث الدلالي: {str(e)}")
            return []
    
    def retrieve_by_family(self, family: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve notes by fragrance family
        
        Args:
            family: Fragrance family (e.g., "Citrus", "Floral", "Woody")
            top_k: Maximum number of results
        
        Returns:
            List of notes from the specified family
        """
        if not self.notes_db:
            return []
        
        try:
            family_lower = family.lower()
            results = [note for note in self.notes_db 
                      if family_lower in note['family'].lower()]
            
            for note in results:
                note['retrieval_method'] = 'family_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب العائلة: {str(e)}")
            return []
    
    def retrieve_by_role(self, role: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve notes by their role in fragrance (Top, Heart, Base)
        
        Args:
            role: Role type (Top, Heart, or Base)
            top_k: Maximum number of results
        
        Returns:
            List of notes with specified role
        """
        if not self.notes_db:
            return []
        
        try:
            role_lower = role.lower()
            results = [note for note in self.notes_db 
                      if role_lower in note['role'].lower()]
            
            for note in results:
                note['retrieval_method'] = 'role_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب الدور: {str(e)}")
            return []
    
    def retrieve_by_use_case(self, use_case: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve notes suitable for specific use cases
        
        Args:
            use_case: Use case (e.g., "summer", "evening", "formal", "daytime")
            top_k: Maximum number of results
        
        Returns:
            List of notes suitable for the use case
        """
        if not self.notes_db:
            return []
        
        try:
            use_case_lower = use_case.lower()
            results = []
            
            for note in self.notes_db:
                if any(use_case_lower in case.lower() for case in note['best_for']):
                    results.append(note)
            
            for note in results:
                note['retrieval_method'] = 'use_case_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب الاستخدام: {str(e)}")
            return []
    
    def hybrid_retrieve(self, query: str, filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict]:
        """
        Hybrid retrieval combining semantic search with optional filters
        
        Args:
            query: Query string
            filters: Optional filters (family, role, use_case)
            top_k: Maximum number of results
        
        Returns:
            List of relevant notes
        """
        try:
            # Start with semantic search
            results = self.retrieve_by_similarity(query, top_k * 2)
            
            # Apply filters if provided
            if filters:
                if 'family' in filters and filters['family']:
                    family_results = self.retrieve_by_family(filters['family'], top_k * 2)
                    family_ids = {n['note'] for n in family_results}
                    results = [n for n in results if n['note'] in family_ids]
                
                if 'role' in filters and filters['role']:
                    role_results = self.retrieve_by_role(filters['role'], top_k * 2)
                    role_ids = {n['note'] for n in role_results}
                    results = [n for n in results if n['note'] in role_ids]
                
                if 'use_case' in filters and filters['use_case']:
                    use_case_results = self.retrieve_by_use_case(filters['use_case'], top_k * 2)
                    use_case_ids = {n['note'] for n in use_case_results}
                    results = [n for n in results if n['note'] in use_case_ids]
            
            # Sort by similarity and return top K
            results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"⚠ خطأ في البحث الهجين: {str(e)}")
            return []
    
    def get_note_details(self, note_name: str) -> Optional[Dict]:
        """Get full details of a specific note"""
        try:
            note_lower = note_name.lower()
            for note in self.notes_db:
                if (note_lower == note['note'].lower() or 
                    note_lower == note['arabic'].lower()):
                    return note.copy()
            return None
        except Exception as e:
            print(f"⚠ خطأ في جلب تفاصيل النوتة: {str(e)}")
            return None
    
    def is_ready(self) -> bool:
        """Check if retriever is ready to use"""
        return (self.index is not None and 
                self.notes_db and 
                self.metadata is not None)


# Global instance
_retriever = None

def get_retriever() -> NotesRetriever:
    """Get or create singleton retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = NotesRetriever()
    return _retriever


# Convenience functions
def retrieve_notes(query: str, top_k: int = 5) -> List[Dict]:
    """Retrieve notes similar to query"""
    retriever = get_retriever()
    if not retriever.is_ready():
        return []
    return retriever.retrieve_by_similarity(query, top_k)


def retrieve_notes_by_family(family: str, top_k: int = 5) -> List[Dict]:
    """Retrieve notes by family"""
    retriever = get_retriever()
    if not retriever.is_ready():
        return []
    return retriever.retrieve_by_family(family, top_k)


def retrieve_notes_by_role(role: str, top_k: int = 5) -> List[Dict]:
    """Retrieve notes by role"""
    retriever = get_retriever()
    if not retriever.is_ready():
        return []
    return retriever.retrieve_by_role(role, top_k)


def retrieve_notes_by_use_case(use_case: str, top_k: int = 5) -> List[Dict]:
    """Retrieve notes by use case"""
    retriever = get_retriever()
    if not retriever.is_ready():
        return []
    return retriever.retrieve_by_use_case(use_case, top_k)


def hybrid_retrieve(query: str, filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict]:
    """Hybrid retrieval with optional filters"""
    retriever = get_retriever()
    if not retriever.is_ready():
        return []
    return retriever.hybrid_retrieve(query, filters, top_k)


def get_note_context(query: str, top_k: int = 5) -> str:
    """
    Get RAG context string for injection into AI prompts
    """
    notes = retrieve_notes(query, top_k)
    
    if not notes:
        return "لم يتم العثور على نوتات ذات صلة"
    
    context = "📚 النوتات المسترجعة من قاعدة المعرفة:\n" + "=" * 50 + "\n"
    
    for i, note in enumerate(notes, 1):
        score = note.get('similarity_score', 0)
        context += f"""
{i}. {note['arabic']} ({note['note']})
   العائلة: {note['family']} | الدور: {note['role']}
   الملف: {note['profile']}
   التطاير: {note['volatility']}
   مناسبة للـ: {', '.join(note['best_for'][:2])}
   الثقة: {score:.1%}
"""
    
    context += "=" * 50 + "\n"
    return context
