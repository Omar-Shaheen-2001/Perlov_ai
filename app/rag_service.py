import json
import os
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

class FragranceKnowledgeBase:
    """
    RAG (Retrieval Augmented Generation) system for fragrance notes.
    Loads and searches a knowledge base of fragrance notes.
    """
    
    def __init__(self, kb_path: str = "notes_kb.json"):
        """Initialize the knowledge base from JSON file"""
        self.kb_path = kb_path
        self.notes_db = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load fragrance notes from the knowledge base JSON file"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                self.notes_db = json.load(f)
            print(f"✓ تم تحميل قاعدة النوتات: {len(self.notes_db)} نوتة")
        except FileNotFoundError:
            print(f"⚠ تنبيه: لم يتم العثور على ملف قاعدة النوتات: {self.kb_path}")
            self.notes_db = []
        except json.JSONDecodeError:
            print(f"⚠ خطأ: فشل تحليل ملف JSON")
            self.notes_db = []
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def search_note(self, query: str, threshold: float = 0.3) -> Dict:
        """
        Search for a specific fragrance note by name.
        Returns exact match or best fuzzy match.
        """
        if not self.notes_db:
            return None
        
        query_lower = query.lower().strip()
        
        # Exact match (English or Arabic)
        for note in self.notes_db:
            if query_lower == note['note'].lower() or query_lower == note['arabic'].lower():
                return note
        
        # Fuzzy match
        best_match = None
        best_score = threshold
        
        for note in self.notes_db:
            # Check against English name
            score_en = self.similarity_score(query, note['note'])
            if score_en > best_score:
                best_score = score_en
                best_match = note
            
            # Check against Arabic name
            score_ar = self.similarity_score(query, note['arabic'])
            if score_ar > best_score:
                best_score = score_ar
                best_match = note
        
        return best_match
    
    def search_by_family(self, family: str) -> List[Dict]:
        """Search all notes by fragrance family"""
        if not self.notes_db:
            return []
        
        family_lower = family.lower()
        results = [note for note in self.notes_db 
                   if family_lower in note['family'].lower()]
        return results
    
    def search_by_role(self, role: str) -> List[Dict]:
        """Search all notes by role (Top, Heart, Base)"""
        if not self.notes_db:
            return []
        
        role_lower = role.lower()
        results = [note for note in self.notes_db 
                   if role_lower in note['role'].lower()]
        return results
    
    def search_by_volatility(self, volatility: str) -> List[Dict]:
        """Search notes by volatility level"""
        if not self.notes_db:
            return []
        
        volatility_lower = volatility.lower()
        results = [note for note in self.notes_db 
                   if volatility_lower in note['volatility'].lower()]
        return results
    
    def search_notes_combination(self, note_list: List[str]) -> Dict:
        """
        Check compatibility between multiple notes.
        Returns compatibility analysis and recommendations.
        """
        if not self.notes_db or not note_list:
            return {"compatible": False, "notes_found": []}
        
        found_notes = []
        for query_note in note_list:
            note = self.search_note(query_note)
            if note:
                found_notes.append(note)
        
        if not found_notes:
            return {"compatible": False, "notes_found": []}
        
        # Check compatibility
        compatible_pairs = 0
        incompatible_pairs = 0
        compatibility_details = []
        
        for i, note1 in enumerate(found_notes):
            for note2 in found_notes[i+1:]:
                # Check if notes work well together
                note2_english = note2['note'].lower()
                note2_arabic = note2['arabic'].lower()
                
                works_well = (note2_english in [n.lower() for n in note1['works_well_with']] or
                             note2_arabic in note1['works_well_with'])
                
                avoid = (note2_english in [n.lower() for n in note1['avoid_with']] or
                        note2_arabic in note1['avoid_with'])
                
                if works_well:
                    compatible_pairs += 1
                    compatibility_details.append({
                        "note1": note1['arabic'],
                        "note2": note2['arabic'],
                        "compatibility": "ممتازة",
                        "reason": f"{note1['arabic']} يعمل بشكل جيد مع {note2['arabic']}"
                    })
                elif avoid:
                    incompatible_pairs += 1
                    compatibility_details.append({
                        "note1": note1['arabic'],
                        "note2": note2['arabic'],
                        "compatibility": "ضعيفة",
                        "reason": f"تجنب دمج {note1['arabic']} مع {note2['arabic']}"
                    })
        
        return {
            "compatible": compatible_pairs > incompatible_pairs,
            "notes_found": found_notes,
            "compatible_pairs": compatible_pairs,
            "incompatible_pairs": incompatible_pairs,
            "compatibility_details": compatibility_details
        }
    
    def get_note_context(self, note_query: str) -> str:
        """
        Get detailed context about a fragrance note for RAG injection.
        Returns formatted text ready to be injected into prompts.
        """
        note = self.search_note(note_query)
        if not note:
            return f"لم يتم العثور على معلومات عن النوتة: {note_query}"
        
        context = f"""
📌 معلومات النوتة: {note['arabic']} ({note['note']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• العائلة العطرية: {note['family']}
• الدور في العطر: {note['role']}
• التطاير: {note['volatility']}
• الملف الشخصي: {note['profile']}
• التركيز المناسب: {note['concentration']}
• الأصل: {note['origin']}

✓ تعمل بشكل جيد مع:
  {', '.join(note['works_well_with'])}

✗ تجنب دمجها مع:
  {', '.join(note['avoid_with'])}

🎯 مناسبة للاستخدام في:
  {', '.join(note['best_for'])}
"""
        return context.strip()
    
    def get_combined_context(self, note_queries: List[str]) -> str:
        """
        Get combined context for multiple notes.
        Useful for creating complex fragrances.
        """
        if not note_queries:
            return "لم يتم تحديد أي نوتات"
        
        contexts = []
        for query in note_queries:
            context = self.get_note_context(query)
            contexts.append(context)
        
        combined = "\n\n".join(contexts)
        
        # Add compatibility analysis
        compatibility = self.search_notes_combination(note_queries)
        if compatibility['compatibility_details']:
            combined += "\n\n📊 تحليل التوافقية:\n"
            combined += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for detail in compatibility['compatibility_details']:
                combined += f"• {detail['reason']}\n"
        
        return combined
    
    def recommend_similar_notes(self, note_query: str, limit: int = 3) -> List[Dict]:
        """
        Recommend notes similar to a given note.
        Based on family, role, and profile similarity.
        """
        base_note = self.search_note(note_query)
        if not base_note:
            return []
        
        similar_notes = []
        
        for note in self.notes_db:
            if note['note'] == base_note['note']:
                continue
            
            # Score based on shared properties
            score = 0
            
            # Same family = high score
            if note['family'] == base_note['family']:
                score += 3
            
            # Same role = medium score
            if note['role'] == base_note['role']:
                score += 2
            
            # Similar volatility = low score
            if note['volatility'] == base_note['volatility']:
                score += 1
            
            if score > 0:
                similar_notes.append((note, score))
        
        # Sort by score and return top matches
        similar_notes.sort(key=lambda x: x[1], reverse=True)
        return [note for note, score in similar_notes[:limit]]
    
    def get_prompt_injection(self, note_queries: List[str]) -> str:
        """
        Generate RAG prompt injection text.
        This is injected into AI prompts for better recommendations.
        """
        if not note_queries:
            return ""
        
        context = self.get_combined_context(note_queries)
        
        injection = f"""
═══════════════════════════════════════════════════════════════
🔍 معلومات من قاعدة المعرفة (RAG - Knowledge Base):
═══════════════════════════════════════════════════════════════

{context}

═══════════════════════════════════════════════════════════════
استخدم المعلومات أعلاه لتقديم توصيات أكثر دقة وملاءمة.
═══════════════════════════════════════════════════════════════
"""
        return injection
    
    def get_family_recommendations(self, families: List[str]) -> List[Dict]:
        """Get all notes from specified fragrance families"""
        if not families:
            return []
        
        results = []
        for family in families:
            family_notes = self.search_by_family(family)
            results.extend(family_notes)
        
        return results
    
    def search_best_for(self, use_case: str) -> List[Dict]:
        """
        Find notes that are best for a specific use case.
        Use cases: summer, winter, evening, daytime, formal, casual, etc.
        """
        if not self.notes_db:
            return []
        
        use_case_lower = use_case.lower()
        results = []
        
        for note in self.notes_db:
            if any(use_case_lower in case.lower() for case in note['best_for']):
                results.append(note)
        
        return results

# Create a global instance of the knowledge base
def get_kb():
    """Get the singleton knowledge base instance"""
    if not hasattr(get_kb, '_instance'):
        get_kb._instance = FragranceKnowledgeBase()
    return get_kb._instance


# Helper functions for easy access
def search_fragrance_note(note_name: str) -> Dict:
    """Search for a fragrance note"""
    kb = get_kb()
    return kb.search_note(note_name)


def get_note_info(note_name: str) -> str:
    """Get detailed information about a note for RAG injection"""
    kb = get_kb()
    return kb.get_note_context(note_name)


def get_rag_context(notes: List[str]) -> str:
    """Get combined RAG context for multiple notes"""
    kb = get_kb()
    return kb.get_prompt_injection(notes)


def check_note_compatibility(notes: List[str]) -> Dict:
    """Check if notes work well together"""
    kb = get_kb()
    return kb.search_notes_combination(notes)


def get_similar_notes(note_name: str, limit: int = 3) -> List[Dict]:
    """Get similar notes recommendations"""
    kb = get_kb()
    return kb.recommend_similar_notes(note_name, limit)


def get_notes_by_family(family: str) -> List[Dict]:
    """Get all notes from a specific family"""
    kb = get_kb()
    return kb.search_by_family(family)


def get_notes_for_use_case(use_case: str) -> List[Dict]:
    """Get notes suitable for a specific use case"""
    kb = get_kb()
    return kb.search_best_for(use_case)
