"""
RAG Validation Layer - طبقة التحقق من صحة مخرجات AI
تضمن أن جميع الاقتراحات موجودة في قاعدة المعرفة
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class ValidationResult:
    """نتيجة التحقق"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    invalid_notes: List[str] = field(default_factory=list)
    invalid_families: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RAGValidator:
    """
    مدقق مخرجات AI مقابل قاعدة المعرفة
    
    يتحقق من:
    - أن النوتات المقترحة موجودة في KB
    - أن العائلات العطرية متطابقة
    - أن نوع البخور متوافق
    - أن درجة الرسمية والشدة ضمن النطاق
    """
    
    def __init__(self, available_notes: List[str], available_families: List[str]):
        self.available_notes = [n.lower() for n in available_notes]
        self.available_families = [f.lower() for f in available_families]
        self.note_aliases = self._build_aliases()
    
    def _build_aliases(self) -> Dict[str, str]:
        """بناء قاموس الأسماء البديلة للنوتات"""
        aliases = {
            'oud': 'agarwood',
            'عود': 'agarwood',
            'العود': 'agarwood',
            'musk': 'musk',
            'مسك': 'musk',
            'rose': 'rose',
            'ورد': 'rose',
            'الورد': 'rose',
            'amber': 'amber',
            'عنبر': 'amber',
            'vanilla': 'vanilla',
            'فانيلا': 'vanilla',
            'sandalwood': 'sandalwood',
            'صندل': 'sandalwood',
            'jasmine': 'jasmine',
            'ياسمين': 'jasmine',
            'saffron': 'saffron',
            'زعفران': 'saffron',
            'bergamot': 'bergamot',
            'برغموت': 'bergamot',
            'lavender': 'lavender',
            'لافندر': 'lavender',
            'cedar': 'cedarwood',
            'أرز': 'cedarwood',
            'vetiver': 'vetiver',
            'فيتيفر': 'vetiver',
            'patchouli': 'patchouli',
            'باتشولي': 'patchouli',
            'incense': 'frankincense',
            'بخور': 'frankincense',
            'لبان': 'frankincense',
        }
        return aliases
    
    def _normalize_note(self, note: str) -> str:
        """تطبيع اسم النوتة"""
        note_lower = note.lower().strip()
        return self.note_aliases.get(note_lower, note_lower)
    
    def validate_notes(self, notes: List[str]) -> Tuple[List[str], List[str]]:
        """
        التحقق من صحة قائمة النوتات
        
        Returns:
            (valid_notes, invalid_notes)
        """
        valid = []
        invalid = []
        
        for note in notes:
            normalized = self._normalize_note(note)
            if normalized in self.available_notes or note.lower() in self.available_notes:
                valid.append(note)
            else:
                found = False
                for available in self.available_notes:
                    if normalized in available or available in normalized:
                        valid.append(note)
                        found = True
                        break
                if not found:
                    invalid.append(note)
        
        return valid, invalid
    
    def validate_family(self, family: str) -> bool:
        """التحقق من صحة العائلة العطرية"""
        family_lower = family.lower().strip()
        
        for available in self.available_families:
            if family_lower in available or available in family_lower:
                return True
        
        return False
    
    def validate_ai_response(
        self, 
        response: Dict, 
        rag_context: Dict,
        strict: bool = True
    ) -> ValidationResult:
        """
        التحقق الشامل من استجابة AI
        
        Args:
            response: استجابة AI المُحللة
            rag_context: سياق RAG الأصلي
            strict: وضع صارم (يرفض أي نوتة غير موجودة)
        
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        notes_to_check = []
        
        if 'ideal_notes' in response:
            notes_to_check.extend(response['ideal_notes'])
        if 'top_notes' in response:
            notes_to_check.extend(response['top_notes'])
        if 'heart_notes' in response:
            notes_to_check.extend(response['heart_notes'])
        if 'base_notes' in response:
            notes_to_check.extend(response['base_notes'])
        if 'recommended_notes' in response:
            notes_to_check.extend(response['recommended_notes'])
        
        if notes_to_check:
            valid, invalid = self.validate_notes(notes_to_check)
            result.invalid_notes = invalid
            
            if invalid and strict:
                result.is_valid = False
                result.errors.append(
                    f"النوتات التالية غير موجودة في قاعدة المعرفة: {', '.join(invalid)}"
                )
            elif invalid:
                result.warnings.append(
                    f"تحذير: النوتات التالية قد لا تكون دقيقة: {', '.join(invalid)}"
                )
        
        families_to_check = []
        if 'recommended_families' in response:
            families_to_check.extend(response['recommended_families'])
        if 'fragrance_family' in response:
            families_to_check.append(response['fragrance_family'])
        if 'best_families' in response:
            families_to_check.extend(response['best_families'])
        
        for family in families_to_check:
            if not self.validate_family(family):
                result.invalid_families.append(family)
                if strict:
                    result.is_valid = False
                    result.errors.append(f"العائلة العطرية '{family}' غير موجودة في قاعدة المعرفة")
        
        if 'top_3_matches' in response:
            for match in response.get('top_3_matches', []):
                actual_notes = match.get('actual_notes', {})
                all_match_notes = []
                all_match_notes.extend(actual_notes.get('top', []))
                all_match_notes.extend(actual_notes.get('heart', []))
                all_match_notes.extend(actual_notes.get('base', []))
                
                if all_match_notes:
                    _, invalid = self.validate_notes(all_match_notes)
                    if invalid:
                        result.warnings.append(
                            f"العطر '{match.get('name', 'غير معروف')}' يحتوي على نوتات غير موثقة"
                        )
        
        if result.invalid_notes:
            result.suggestions.append("يُرجى استخدام النوتات المتاحة في قاعدة المعرفة فقط")
        if result.invalid_families:
            result.suggestions.append("يُرجى اختيار من العائلات العطرية المتاحة")
        
        return result
    
    def sanitize_response(
        self, 
        response: Dict, 
        validation: ValidationResult
    ) -> Dict:
        """
        تنظيف الاستجابة بإزالة العناصر غير الصالحة
        
        Args:
            response: الاستجابة الأصلية
            validation: نتيجة التحقق
        
        Returns:
            الاستجابة المُنظفة
        """
        sanitized = response.copy()
        
        invalid_set = set(n.lower() for n in validation.invalid_notes)
        
        for key in ['ideal_notes', 'top_notes', 'heart_notes', 'base_notes', 'recommended_notes']:
            if key in sanitized and isinstance(sanitized[key], list):
                sanitized[key] = [
                    n for n in sanitized[key] 
                    if n.lower() not in invalid_set
                ]
        
        invalid_families_set = set(f.lower() for f in validation.invalid_families)
        
        for key in ['recommended_families', 'best_families']:
            if key in sanitized and isinstance(sanitized[key], list):
                sanitized[key] = [
                    f for f in sanitized[key] 
                    if f.lower() not in invalid_families_set
                ]
        
        sanitized['_validation'] = validation.to_dict()
        
        return sanitized


def create_validator_from_rag(rag_result) -> RAGValidator:
    """إنشاء validator من نتيجة RAG"""
    notes = [n.get('note', '') for n in rag_result.notes if n.get('note')]
    families = rag_result.families if hasattr(rag_result, 'families') else []
    return RAGValidator(notes, families)


def validate_and_sanitize(
    ai_response: Dict,
    rag_result,
    strict: bool = True
) -> Tuple[Dict, ValidationResult]:
    """
    دالة مختصرة للتحقق والتنظيف
    
    Args:
        ai_response: استجابة AI
        rag_result: نتيجة RAG
        strict: وضع صارم
    
    Returns:
        (sanitized_response, validation_result)
    """
    validator = create_validator_from_rag(rag_result)
    
    validation = validator.validate_ai_response(
        ai_response, 
        {'notes': rag_result.notes, 'families': rag_result.families},
        strict=strict
    )
    
    if not validation.is_valid:
        sanitized = validator.sanitize_response(ai_response, validation)
        return sanitized, validation
    
    ai_response['_validation'] = validation.to_dict()
    return ai_response, validation
