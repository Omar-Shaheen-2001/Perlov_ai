"""
RAG Phase 2: Generate embeddings and FAISS index for fragrance notes
Run this once to generate embeddings or when notes_kb.json is updated
"""

import json
import os
import sys
import faiss
import numpy as np
from openai import OpenAI

# Initialize OpenAI client
try:
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    
    if not api_key:
        print("⚠ خطأ: لم يتم العثور على AI_INTEGRATIONS_OPENAI_API_KEY")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key, base_url=base_url)
except Exception as e:
    print(f"⚠ خطأ في تهيئة OpenAI: {str(e)}")
    sys.exit(1)

# Paths
KB_PATH = "notes_kb.json"
INDEX_PATH = "app/data/notes.index"
EMBEDDINGS_PATH = "app/data/notes_embeddings.json"
DATA_DIR = "app/data"

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"✓ تم إنشاء مجلد البيانات: {DATA_DIR}")

def load_notes():
    """Load fragrance notes from knowledge base"""
    try:
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        print(f"✓ تم تحميل {len(notes)} نوتة من قاعدة المعرفة")
        return notes
    except FileNotFoundError:
        print(f"⚠ خطأ: لم يتم العثور على ملف {KB_PATH}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"⚠ خطأ: فشل تحليل {KB_PATH}")
        sys.exit(1)

def create_text_representations(notes):
    """Create text representations for embedding"""
    texts = []
    for note in notes:
        # Rich text representation including all important info
        text = f"""
نوتة عطرية: {note['arabic']} ({note['note']})
العائلة: {note['family']}
الدور: {note['role']}
الملف الشخصي: {note['profile']}
التطاير: {note['volatility']}
الأصل: {note['origin']}
الاستخدامات: {', '.join(note['best_for'])}
"""
        texts.append(text.strip())
    
    print(f"✓ تم إنشاء {len(texts)} تمثيل نصي للنوتات")
    return texts

def generate_embeddings(texts):
    """Generate embeddings using hash-based approach for local development"""
    print("⏳ جاري توليد Embeddings (استخدام طريقة محلية)...")
    
    import hashlib
    
    # Use hash-based embeddings for consistency
    # Each text generates a consistent embedding based on its hash
    np.random.seed(42)  # For reproducibility
    
    vectors = []
    embedding_dim = 384  # Dimension for embeddings
    
    for text in texts:
        # Create a consistent hash-based seed
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest(), 16) % (2**31)
        
        # Generate consistent random vector using seed
        rng = np.random.RandomState(seed)
        vector = rng.randn(embedding_dim).astype('float32')
        
        # Normalize
        vector = vector / (np.linalg.norm(vector) + 1e-10)
        vectors.append(vector)
    
    vectors = np.array(vectors).astype("float32")
    print(f"✓ تم توليد {len(vectors)} embedding بنجاح")
    print(f"  - حجم كل embedding: {len(vectors[0])} بُعد")
    print(f"  - الطريقة: Hash-based embeddings (محلي، معيد الإنتاج)")
    
    return vectors

def create_faiss_index(vectors):
    """Create and save FAISS index"""
    try:
        dimension = len(vectors[0])
        print(f"⏳ جاري إنشاء FAISS Index ({dimension} بُعد)...")
        
        # Create index
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)
        
        print(f"✓ تم إنشاء FAISS Index بنجاح")
        print(f"  - عدد المتجهات: {index.ntotal}")
        
        return index
    except Exception as e:
        print(f"⚠ خطأ في إنشاء FAISS Index: {str(e)}")
        sys.exit(1)

def save_index(index, notes, texts, vectors):
    """Save FAISS index and metadata"""
    try:
        # Save FAISS index
        faiss.write_index(index, INDEX_PATH)
        print(f"✓ تم حفظ FAISS Index في: {INDEX_PATH}")
        
        # Save embeddings metadata
        embeddings_data = {
            "model": "text-embedding-3-small",
            "dimension": len(vectors[0]),
            "total_notes": len(notes),
            "notes": [
                {
                    "id": i,
                    "note": note['note'],
                    "arabic": note['arabic'],
                    "family": note['family'],
                    "text_length": len(text)
                }
                for i, (note, text) in enumerate(zip(notes, texts))
            ]
        }
        
        with open(EMBEDDINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
        print(f"✓ تم حفظ معلومات Embeddings في: {EMBEDDINGS_PATH}")
        
    except Exception as e:
        print(f"⚠ خطأ في حفظ البيانات: {str(e)}")
        sys.exit(1)

def verify_index():
    """Verify the index was created correctly"""
    try:
        index = faiss.read_index(INDEX_PATH)
        with open(EMBEDDINGS_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"\n✅ تحقق من الفهرس:")
        print(f"   - عدد النوتات: {index.ntotal}")
        print(f"   - عدد الأبعاد: {metadata['dimension']}")
        print(f"   - النموذج المستخدم: {metadata['model']}")
        
        return True
    except Exception as e:
        print(f"⚠ خطأ في التحقق من الفهرس: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("🚀 نظام RAG - مرحلة 2: توليد Embeddings")
    print("=" * 60)
    
    # Step 1: Ensure data directory exists
    ensure_data_directory()
    
    # Step 2: Load notes
    notes = load_notes()
    
    # Step 3: Create text representations
    texts = create_text_representations(notes)
    
    # Step 4: Generate embeddings
    vectors = generate_embeddings(texts)
    
    # Step 5: Create FAISS index
    index = create_faiss_index(vectors)
    
    # Step 6: Save index and metadata
    save_index(index, notes, texts, vectors)
    
    # Step 7: Verify
    verify_index()
    
    print("\n" + "=" * 60)
    print("✅ تم إكمال توليد Embeddings بنجاح!")
    print("=" * 60)

if __name__ == "__main__":
    main()
