"""
RAG Engine - المحرك الموحد لنظام RAG
يوفر واجهة مركزية لجميع عمليات الاسترجاع والتحقق
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from app.notes_retriever import (
    retrieve_notes, 
    hybrid_retrieve, 
    retrieve_notes_by_family,
    retrieve_notes_by_role,
    get_retriever
)


@dataclass
class RAGResult:
    """نتيجة استعلام RAG"""
    notes: List[Dict] = field(default_factory=list)
    context_text: str = ""
    note_ids: List[str] = field(default_factory=list)
    families: List[str] = field(default_factory=list)
    is_valid: bool = True
    debug_info: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RAGDebugInfo:
    """معلومات التصحيح لنظام RAG"""
    query: str = ""
    module_type: str = ""
    retrieved_count: int = 0
    used_notes: List[Dict] = field(default_factory=list)
    excluded_notes: List[Dict] = field(default_factory=list)
    selection_reasons: List[str] = field(default_factory=list)
    exclusion_reasons: List[str] = field(default_factory=list)
    filters_applied: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RAGEngine:
    """
    RAG Engine - المحرك الموحد لنظام RAG
    
    يوفر:
    - استرجاع موحد للنوتات
    - فلترة متقدمة
    - توليد السياق للـ AI
    - وضع التصحيح (Debug Mode)
    """
    
    STRICT_PROMPT_TEMPLATE = """
⚠️ تعليمات صارمة - Source of Truth:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 ممنوع تماماً:
• اقتراح أي نوتة عطرية غير موجودة في القائمة أدناه
• ذكر أي عطر أو علامة تجارية غير مدعومة بالنوتات المسترجعة
• اختراع أو تخمين معلومات غير موجودة في السياق

✅ مطلوب:
• استخدام النوتات المسترجعة فقط كمصدر وحيد للحقيقة
• إذا لم تجد نوتات مناسبة، أعد استجابة تعليمية عامة بدون أسماء محددة
• التزم بالعائلات العطرية المذكورة فقط

📚 النوتات المتاحة من قاعدة المعرفة:
{notes_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    MODULE_CONFIGS = {
        'scent_dna': {
            'top_k': 6,
            'include_families': True,
            'require_validation': True
        },
        'custom_perfume': {
            'top_k': 8,
            'include_families': True,
            'require_validation': True
        },
        'recommendations': {
            'top_k': 10,
            'include_families': True,
            'require_validation': True
        },
        'article': {
            'top_k': 5,
            'include_families': False,
            'require_validation': False
        },
        'face_analyzer': {
            'top_k': 6,
            'include_families': True,
            'require_validation': True
        },
        'blend_predictor': {
            'top_k': 8,
            'include_families': True,
            'require_validation': True
        },
        'default': {
            'top_k': 5,
            'include_families': True,
            'require_validation': True
        }
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._retriever = get_retriever()
    
    def run(
        self,
        query: str,
        filters: Optional[Dict] = None,
        module_type: str = 'default',
        top_k: Optional[int] = None,
        debug: Optional[bool] = None
    ) -> RAGResult:
        """
        تنفيذ استعلام RAG موحد
        
        Args:
            query: استعلام البحث
            filters: فلاتر اختيارية (family, role, incense_style, formality)
            module_type: نوع الوحدة (scent_dna, custom_perfume, etc.)
            top_k: عدد النتائج (اختياري، يستخدم إعداد الوحدة افتراضياً)
            debug: تفعيل وضع التصحيح
        
        Returns:
            RAGResult مع النوتات والسياق ومعلومات التصحيح
        """
        use_debug = debug if debug is not None else self.debug
        config = self.MODULE_CONFIGS.get(module_type, self.MODULE_CONFIGS['default'])
        k = top_k or config['top_k']
        
        debug_info = RAGDebugInfo(
            query=query,
            module_type=module_type,
            filters_applied=filters or {}
        ) if use_debug else None
        
        try:
            if filters:
                notes = hybrid_retrieve(query, filters, k)
            else:
                notes = retrieve_notes(query, k)
            
            if not notes:
                return RAGResult(
                    notes=[],
                    context_text=self._generate_empty_context(),
                    is_valid=False,
                    debug_info=debug_info.to_dict() if debug_info else {}
                )
            
            notes = self._apply_advanced_filters(notes, filters, debug_info)
            
            note_ids = [n.get('note', n.get('name_en', '')) for n in notes]
            families = list(set(n.get('family', '') for n in notes if n.get('family')))
            
            context_text = self._generate_context(notes, config)
            strict_context = self.STRICT_PROMPT_TEMPLATE.format(notes_context=context_text)
            
            if debug_info:
                debug_info.retrieved_count = len(notes)
                debug_info.used_notes = [
                    {'name': n.get('note'), 'family': n.get('family'), 'score': n.get('similarity_score', 1.0)}
                    for n in notes
                ]
                debug_info.selection_reasons = [
                    f"تم اختيار {n.get('arabic')} بسبب التطابق مع الاستعلام (score: {n.get('similarity_score', 1.0):.2f})"
                    for n in notes[:3]
                ]
            
            return RAGResult(
                notes=notes,
                context_text=strict_context,
                note_ids=note_ids,
                families=families,
                is_valid=True,
                debug_info=debug_info.to_dict() if debug_info else {}
            )
            
        except Exception as e:
            if debug_info:
                debug_info.exclusion_reasons.append(f"خطأ في الاسترجاع: {str(e)}")
            
            return RAGResult(
                notes=[],
                context_text=self._generate_empty_context(),
                is_valid=False,
                debug_info=debug_info.to_dict() if debug_info else {'error': str(e)}
            )
    
    def _apply_advanced_filters(
        self, 
        notes: List[Dict], 
        filters: Optional[Dict],
        debug_info: Optional[RAGDebugInfo]
    ) -> List[Dict]:
        """تطبيق فلاتر متقدمة على النوتات"""
        if not filters:
            return notes
        
        filtered = notes.copy()
        
        if 'incense_style' in filters and filters['incense_style']:
            target_style = filters['incense_style'].lower()
            before_count = len(filtered)
            filtered = [
                n for n in filtered 
                if target_style in n.get('incense_style', 'clean').lower()
            ]
            if debug_info and before_count != len(filtered):
                debug_info.exclusion_reasons.append(
                    f"تم استبعاد {before_count - len(filtered)} نوتات بسبب عدم تطابق نمط البخور"
                )
        
        if 'min_formality' in filters:
            min_score = filters['min_formality']
            before_count = len(filtered)
            filtered = [
                n for n in filtered 
                if n.get('formality_score', 5) >= min_score
            ]
            if debug_info and before_count != len(filtered):
                debug_info.exclusion_reasons.append(
                    f"تم استبعاد {before_count - len(filtered)} نوتات بسبب درجة الرسمية"
                )
        
        if 'max_intensity' in filters:
            max_weight = filters['max_intensity']
            before_count = len(filtered)
            filtered = [
                n for n in filtered 
                if n.get('intensity_weight', 5) <= max_weight
            ]
            if debug_info and before_count != len(filtered):
                debug_info.exclusion_reasons.append(
                    f"تم استبعاد {before_count - len(filtered)} نوتات بسبب شدة العطر"
                )
        
        return filtered if filtered else notes[:3]
    
    def _generate_context(self, notes: List[Dict], config: Dict) -> str:
        """توليد نص السياق للحقن في البرومبت"""
        if not notes:
            return self._generate_empty_context()
        
        context_parts = []
        
        for i, note in enumerate(notes, 1):
            works_with = note.get('works_well_with', [])
            best_for = note.get('best_for', [])
            avoid = note.get('avoid_with', [])
            
            if isinstance(works_with, list):
                works_with = ', '.join(works_with[:3]) if works_with else 'N/A'
            if isinstance(best_for, list):
                best_for = ', '.join(best_for[:2]) if best_for else 'N/A'
            if isinstance(avoid, list):
                avoid = ', '.join(avoid[:2]) if avoid else 'N/A'
            
            score = note.get('similarity_score', 1.0)
            
            part = f"""
📍 [{i}] {note.get('arabic', '')} ({note.get('note', '')})
   ├─ العائلة: {note.get('family', 'N/A')}
   ├─ الدور: {note.get('role', 'N/A')}
   ├─ التطاير: {note.get('volatility', 'N/A')}
   ├─ الملف: {note.get('profile', 'N/A')}
   ├─ مناسب للـ: {best_for}
   ├─ يعمل مع: {works_with}
   ├─ تجنب مع: {avoid}
   └─ درجة التطابق: {score:.0%}"""
            
            context_parts.append(part)
        
        if config.get('include_families'):
            families = list(set(n.get('family', '') for n in notes if n.get('family')))
            if families:
                context_parts.append(f"\n🏷️ العائلات المتاحة: {', '.join(families)}")
        
        return '\n'.join(context_parts)
    
    def _generate_empty_context(self) -> str:
        """توليد سياق فارغ مع تعليمات"""
        return """
⚠️ لم يتم العثور على نوتات مطابقة في قاعدة المعرفة.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 ممنوع: اقتراح أي نوتة أو عطر محدد
✅ مطلوب: تقديم نصائح عامة تعليمية فقط بدون أسماء محددة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def get_available_notes(self) -> List[str]:
        """الحصول على قائمة النوتات المتاحة"""
        if not self._retriever or not self._retriever.notes_db:
            return []
        return [n.get('note', '') for n in self._retriever.notes_db]
    
    def get_available_families(self) -> List[str]:
        """الحصول على قائمة العائلات المتاحة"""
        if not self._retriever or not self._retriever.notes_db:
            return []
        return list(set(n.get('family', '') for n in self._retriever.notes_db if n.get('family')))
    
    def validate_note_exists(self, note_name: str) -> bool:
        """التحقق من وجود نوتة في قاعدة المعرفة"""
        available = self.get_available_notes()
        note_lower = note_name.lower()
        return any(note_lower == n.lower() for n in available)
    
    def validate_family_exists(self, family_name: str) -> bool:
        """التحقق من وجود عائلة في قاعدة المعرفة"""
        available = self.get_available_families()
        family_lower = family_name.lower()
        return any(family_lower in f.lower() for f in available)


_engine_instance = None


def get_rag_engine(debug: bool = False) -> RAGEngine:
    """الحصول على instance من RAG Engine"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RAGEngine(debug=debug)
    return _engine_instance


def rag_run(
    query: str,
    filters: Optional[Dict] = None,
    module_type: str = 'default',
    top_k: Optional[int] = None,
    debug: bool = False
) -> RAGResult:
    """دالة مختصرة لتشغيل RAG Engine"""
    engine = get_rag_engine(debug)
    return engine.run(query, filters, module_type, top_k, debug)
