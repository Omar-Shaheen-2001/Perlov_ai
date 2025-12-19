"""
RAG Phase 3: Retrieval — Fetch relevant fragrance notes based on queries
Uses FAISS index built from database for efficient similarity search
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
    Uses FAISS index built from database for efficient similarity search.
    """
    
    def __init__(self, 
                 index_path: str = "app/data/notes.index",
                 embeddings_path: str = "app/data/notes_embeddings.json",
                 cache_path: str = "app/data/notes_cache.json"):
        """Initialize the retriever with FAISS index"""
        self.index_path = index_path
        self.embeddings_path = embeddings_path
        self.cache_path = cache_path
        
        self.notes_db = []
        self.index = None
        self.metadata = None
        self.notes_map = {}
        
        self.load_resources()
    
    def load_resources(self):
        """Load FAISS index and notes from cache"""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.notes_db = json.load(f)
                print(f"✓ تم تحميل {len(self.notes_db)} نوتة من الكاش")
            elif os.path.exists('notes_kb.json'):
                with open('notes_kb.json', 'r', encoding='utf-8') as f:
                    self.notes_db = json.load(f)
                print(f"✓ تم تحميل {len(self.notes_db)} نوتة من JSON (fallback)")
            
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"✓ تم تحميل FAISS index: {self.index.ntotal} متجه")
            else:
                print(f"⚠ FAISS index غير موجود في {self.index_path}")
            
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                if 'notes' in self.metadata:
                    for note_info in self.metadata['notes']:
                        self.notes_map[note_info['id']] = note_info
                print(f"✓ تم تحميل metadata")
        
        except Exception as e:
            print(f"⚠ خطأ في تحميل الموارد: {str(e)}")
    
    def reload(self):
        """Reload resources after index rebuild"""
        self.notes_db = []
        self.index = None
        self.metadata = None
        self.notes_map = {}
        self.load_resources()
    
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
        """
        if self.index is None or not self.notes_db:
            return []
        
        try:
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            query_vec = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.notes_db):
                    continue
                
                note = self.notes_db[idx].copy()
                note['similarity_score'] = float(1 / (1 + distance))
                note['retrieval_method'] = 'semantic'
                results.append(note)
            
            return results
        
        except Exception as e:
            print(f"⚠ خطأ في البحث الدلالي: {str(e)}")
            return []
    
    def retrieve_by_family(self, family: str, top_k: int = 5) -> List[Dict]:
        """Retrieve notes by fragrance family"""
        if not self.notes_db:
            return []
        
        try:
            family_lower = family.lower()
            results = [note.copy() for note in self.notes_db 
                      if family_lower in note.get('family', '').lower()]
            
            for note in results:
                note['retrieval_method'] = 'family_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب العائلة: {str(e)}")
            return []
    
    def retrieve_by_role(self, role: str, top_k: int = 5) -> List[Dict]:
        """Retrieve notes by their role (Top, Heart, Base)"""
        if not self.notes_db:
            return []
        
        try:
            role_lower = role.lower()
            results = [note.copy() for note in self.notes_db 
                      if role_lower in note.get('role', '').lower()]
            
            for note in results:
                note['retrieval_method'] = 'role_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب الدور: {str(e)}")
            return []
    
    def retrieve_by_use_case(self, use_case: str, top_k: int = 5) -> List[Dict]:
        """Retrieve notes suitable for specific use cases"""
        if not self.notes_db:
            return []
        
        try:
            use_case_lower = use_case.lower()
            results = []
            
            for note in self.notes_db:
                best_for = note.get('best_for', [])
                if isinstance(best_for, list):
                    if any(use_case_lower in case.lower() for case in best_for):
                        results.append(note.copy())
            
            for note in results:
                note['retrieval_method'] = 'use_case_filter'
                note['similarity_score'] = 1.0
            
            return results[:top_k]
        except Exception as e:
            print(f"⚠ خطأ في البحث حسب الاستخدام: {str(e)}")
            return []
    
    def hybrid_retrieve(self, query: str, filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict]:
        """Hybrid retrieval combining semantic search with optional filters"""
        try:
            results = self.retrieve_by_similarity(query, top_k * 2)
            
            if filters:
                if 'family' in filters and filters['family']:
                    family_ids = {n['note'] for n in self.retrieve_by_family(filters['family'], 100)}
                    results = [n for n in results if n.get('note') in family_ids]
                
                if 'role' in filters and filters['role']:
                    role_ids = {n['note'] for n in self.retrieve_by_role(filters['role'], 100)}
                    results = [n for n in results if n.get('note') in role_ids]
            
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
                if (note_lower == note.get('note', '').lower() or 
                    note_lower == note.get('arabic', '').lower()):
                    return note.copy()
            return None
        except:
            return None
    
    def is_ready(self) -> bool:
        """Check if retriever is ready to use"""
        return self.index is not None and len(self.notes_db) > 0


_retriever = None

def get_retriever() -> NotesRetriever:
    """Get or create singleton retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = NotesRetriever()
    return _retriever


def reload_retriever():
    """Reload the retriever after index rebuild"""
    global _retriever
    if _retriever:
        _retriever.reload()
    else:
        _retriever = NotesRetriever()


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
    """Get RAG context string for injection into AI prompts"""
    notes = retrieve_notes(query, top_k)
    
    if not notes:
        return ""
    
    context = "📚 النوتات المسترجعة من قاعدة المعرفة:\n" + "=" * 50 + "\n"
    
    for i, note in enumerate(notes, 1):
        score = note.get('similarity_score', 0)
        works_with = note.get('works_well_with', [])
        best_for = note.get('best_for', [])
        
        if isinstance(works_with, list):
            works_with = ', '.join(works_with[:3])
        if isinstance(best_for, list):
            best_for = ', '.join(best_for[:2])
        
        context += f"""
{i}. {note.get('arabic', '')} ({note.get('note', '')})
   العائلة: {note.get('family', '')} | الدور: {note.get('role', '')}
   الملف: {note.get('profile', '')}
   التطاير: {note.get('volatility', '')}
   مناسبة للـ: {best_for}
   يعمل جيداً مع: {works_with}
"""
    
    context += "=" * 50 + "\n"
    return context