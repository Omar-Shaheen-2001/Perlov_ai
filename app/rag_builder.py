"""
RAG Builder - Builds FAISS index from database
This module handles building and rebuilding the FAISS index from PerfumeNote database records
"""

import os
import json
import hashlib
import numpy as np
import faiss
from datetime import datetime


def generate_embedding(text: str, embedding_dim: int = 384) -> np.ndarray:
    """Generate consistent hash-based embedding for text"""
    hash_obj = hashlib.md5(text.encode())
    seed = int(hash_obj.hexdigest(), 16) % (2**31)
    
    rng = np.random.RandomState(seed)
    vector = rng.randn(embedding_dim).astype('float32')
    vector = vector / (np.linalg.norm(vector) + 1e-10)
    
    return vector


def create_note_text(note_dict: dict) -> str:
    """Create searchable text representation of a note"""
    parts = [
        note_dict.get('note', ''),
        note_dict.get('arabic', ''),
        note_dict.get('family', ''),
        note_dict.get('role', ''),
        note_dict.get('profile', ''),
        note_dict.get('volatility', '')
    ]
    
    works_with = note_dict.get('works_well_with', [])
    if isinstance(works_with, list):
        parts.extend(works_with)
    
    best_for = note_dict.get('best_for', [])
    if isinstance(best_for, list):
        parts.extend(best_for)
    
    return ' '.join([str(p) for p in parts if p])


def rebuild_faiss_index() -> dict:
    """
    Rebuild FAISS index from database
    
    Returns:
        dict with keys: success, notes_count, error (if failed)
    """
    try:
        from app.models import PerfumeNote
        
        notes = PerfumeNote.get_active_notes()
        notes_dicts = [note.to_dict() for note in notes]
        
        if not notes_dicts:
            return {
                'success': False,
                'error': 'لا توجد نوتات فعّالة في قاعدة البيانات',
                'notes_count': 0
            }
        
        print(f"🔄 جاري إعادة بناء FAISS index من {len(notes_dicts)} نوتة...")
        
        texts = [create_note_text(n) for n in notes_dicts]
        
        embedding_dim = 384
        vectors = []
        for text in texts:
            vector = generate_embedding(text, embedding_dim)
            vectors.append(vector)
        
        vectors = np.array(vectors).astype('float32')
        
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(vectors)
        
        data_dir = 'app/data'
        os.makedirs(data_dir, exist_ok=True)
        
        index_path = os.path.join(data_dir, 'notes.index')
        faiss.write_index(index, index_path)
        
        metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'notes_count': len(notes_dicts),
            'embedding_dim': embedding_dim,
            'source': 'database',
            'notes': [
                {
                    'id': i,
                    'db_id': n['id'],
                    'note': n['note'],
                    'arabic': n['arabic'],
                    'family': n['family']
                }
                for i, n in enumerate(notes_dicts)
            ]
        }
        
        metadata_path = os.path.join(data_dir, 'notes_embeddings.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        notes_cache_path = os.path.join(data_dir, 'notes_cache.json')
        with open(notes_cache_path, 'w', encoding='utf-8') as f:
            json.dump(notes_dicts, f, ensure_ascii=False, indent=2)
        
        global _retriever_instance
        _retriever_instance = None
        
        print(f"✅ تم إعادة بناء FAISS index بنجاح ({len(notes_dicts)} نوتة)")
        
        return {
            'success': True,
            'notes_count': len(notes_dicts),
            'index_path': index_path,
            'metadata_path': metadata_path
        }
    
    except Exception as e:
        print(f"❌ خطأ في إعادة بناء الفهرس: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'notes_count': 0
        }


_retriever_instance = None


def get_notes_from_cache() -> list:
    """Get notes from cache file (faster than database query)"""
    cache_path = 'app/data/notes_cache.json'
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    try:
        from app.models import PerfumeNote
        return PerfumeNote.get_all_notes_as_dict()
    except:
        pass
    
    if os.path.exists('notes_kb.json'):
        with open('notes_kb.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []


def initialize_rag_system():
    """Initialize RAG system on app startup"""
    data_dir = 'app/data'
    index_path = os.path.join(data_dir, 'notes.index')
    
    if not os.path.exists(index_path):
        print("🔄 FAISS index غير موجود، جاري البناء الأولي...")
        
        if os.path.exists('notes_kb.json'):
            try:
                from app.models import PerfumeNote
                import json
                
                with open('notes_kb.json', 'r', encoding='utf-8') as f:
                    notes_data = json.load(f)
                
                for note_data in notes_data:
                    existing = PerfumeNote.query.filter_by(name_en=note_data['note']).first()
                    if not existing:
                        note = PerfumeNote(
                            name_en=note_data['note'],
                            name_ar=note_data['arabic'],
                            family=note_data['family'],
                            role=note_data['role'],
                            volatility=note_data['volatility'],
                            profile=note_data['profile'],
                            works_well_with=json.dumps(note_data.get('works_well_with', []), ensure_ascii=False),
                            avoid_with=json.dumps(note_data.get('avoid_with', []), ensure_ascii=False),
                            best_for=json.dumps(note_data.get('best_for', []), ensure_ascii=False),
                            concentration=note_data.get('concentration', ''),
                            origin=note_data.get('origin', ''),
                            is_active=True
                        )
                        from app import db
                        db.session.add(note)
                
                from app import db
                db.session.commit()
                print(f"✅ تم استيراد النوتات من JSON")
            except Exception as e:
                print(f"⚠ خطأ في استيراد النوتات: {str(e)}")
        
        rebuild_faiss_index()
    else:
        print("✅ FAISS index موجود ومحمّل")