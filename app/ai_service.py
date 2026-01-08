import json
import os
from openai import OpenAI
from flask_login import current_user
from app.rag_service import get_kb, get_rag_context, get_notes_by_family, get_similar_notes
from app.notes_retriever import retrieve_notes, get_note_context as get_retriever_context, hybrid_retrieve, retrieve_notes_by_family, retrieve_notes_by_role
from app.rag_engine import rag_run, get_rag_engine, RAGResult
from app.validators.rag_validation import validate_and_sanitize, RAGValidator
from app.constants.default_responses import get_default_response, get_safe_fallback, VALIDATION_FAILED_RESPONSE

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

MODULE_INFO = {
    'bio_scent': {'name_ar': 'تحليل الرائحة الحيوية', 'icon': 'bi-soundwave'},
    'skin_chemistry': {'name_ar': 'كيمياء البشرة', 'icon': 'bi-droplet'},
    'temp_volatility': {'name_ar': 'التطاير الحراري', 'icon': 'bi-thermometer-half'},
    'metabolism': {'name_ar': 'التمثيل الغذائي', 'icon': 'bi-activity'},
    'climate': {'name_ar': 'محرك المناخ', 'icon': 'bi-cloud-sun'},
    'neuroscience': {'name_ar': 'علم الأعصاب العطري', 'icon': 'bi-brain'},
    'stability': {'name_ar': 'الثبات والانتشار', 'icon': 'bi-clock-history'},
    'predictive': {'name_ar': 'الذكاء التنبّؤي', 'icon': 'bi-magic'},
    'scent_personality': {'name_ar': 'الشخصية العطرية', 'icon': 'bi-person-badge'},
    'signature': {'name_ar': 'العطر التوقيعي', 'icon': 'bi-pen'},
    'occasion': {'name_ar': 'عطر لكل مناسبة', 'icon': 'bi-calendar-event'},
    'habit_planner': {'name_ar': 'الخطة العطرية', 'icon': 'bi-calendar-check'},
    'digital_twin': {'name_ar': 'التوأم الرقمي', 'icon': 'bi-person-bounding-box'},
    'adaptive': {'name_ar': 'العطر التكيّفي', 'icon': 'bi-arrow-repeat'},
    'oil_mixer': {'name_ar': 'مازج الزيوت', 'icon': 'bi-shuffle'},
    'scent_dna': {'name_ar': 'بصمة الرائحة', 'icon': 'bi-fingerprint'},
    'custom_perfume': {'name_ar': 'تصميم عطر مخصص', 'icon': 'bi-palette'},
    'recommendations': {'name_ar': 'توصيات العطور', 'icon': 'bi-stars'},
    'face_analyzer': {'name_ar': 'محلل العطر بالوجه', 'icon': 'bi-camera'}
}

def save_analysis_result(module_type, input_data, result_data):
    """Save analysis result to database for the current user."""
    from app import db
    from app.models import AnalysisResult
    
    if not current_user.is_authenticated:
        return None
    
    module_info = MODULE_INFO.get(module_type, {'name_ar': module_type, 'icon': 'bi-star'})
    
    analysis = AnalysisResult(
        user_id=current_user.id,
        module_type=module_type,
        module_name_ar=module_info['name_ar'],
        module_icon=module_info['icon'],
        input_data=json.dumps(input_data, ensure_ascii=False) if input_data else None,
        result_data=json.dumps(result_data, ensure_ascii=False) if result_data else None
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    return analysis.id

DEBUG_MODE = os.environ.get('RAG_DEBUG', 'false').lower() == 'true'

def get_rag_context_for_ai(query: str, top_k: int = 5, filters: dict = None, module_type: str = 'default', debug: bool = None) -> tuple:
    """
    توليد RAG context موحّد لجميع خدمات الذكاء الاصطناعي باستخدام RAG Engine
    
    Args:
        query: استعلام البحث
        top_k: عدد النتائج المطلوبة
        filters: فلاتر اختيارية (family, role, incense_style)
        module_type: نوع الوحدة (scent_dna, custom_perfume, etc.)
        debug: تفعيل وضع التصحيح
    
    Returns:
        tuple: (context_text, rag_result) - النص المنسق ونتيجة RAG الكاملة
    """
    use_debug = debug if debug is not None else DEBUG_MODE
    
    try:
        rag_result = rag_run(
            query=query,
            filters=filters,
            module_type=module_type,
            top_k=top_k,
            debug=use_debug
        )
        
        return rag_result.context_text, rag_result
    
    except Exception as e:
        print(f"⚠️ RAG Context Error: {str(e)}")
        return "", RAGResult(is_valid=False, debug_info={'error': str(e)})


def validate_ai_output(response: dict, rag_result: RAGResult, module_type: str, strict: bool = True) -> dict:
    """
    التحقق من صحة مخرجات AI مقابل قاعدة المعرفة
    
    Args:
        response: استجابة AI
        rag_result: نتيجة RAG
        module_type: نوع الوحدة
        strict: وضع صارم (يرفض المخالفات)
    
    Returns:
        استجابة مُنظفة أو fallback آمن
    """
    if not rag_result.is_valid or not rag_result.notes:
        return get_safe_fallback(module_type, "لا توجد بيانات RAG كافية")
    
    try:
        sanitized, validation = validate_and_sanitize(response, rag_result, strict=strict)
        
        if not validation.is_valid and strict:
            fallback = get_default_response(module_type)
            fallback['_validation'] = validation.to_dict()
            fallback['_fallback_reason'] = "فشل التحقق من الصحة"
            return fallback
        
        return sanitized
    
    except Exception as e:
        return get_safe_fallback(module_type, str(e))


def parse_ai_response(content):
    """Safely parse AI response content, handling None and malformed JSON."""
    if content is None:
        return None
    
    result = content.strip()
    
    # Try to extract JSON from code blocks first
    if result.startswith("```"):
        parts = result.split("```")
        if len(parts) > 1:
            result = parts[1]
            if result.startswith("json"):
                result = result[4:]
    
    result = result.strip()
    
    # Try to parse the result as JSON
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        pass
    
    # If that fails, try to extract JSON from the text
    # Find the first { and last } and try to parse that
    try:
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = result[start_idx:end_idx + 1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # If still failing, try to find [ and ] for arrays
    try:
        start_idx = result.find('[')
        end_idx = result.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = result[start_idx:end_idx + 1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return None

def get_ai_response(prompt, system_message="أنت خبير عطور محترف. أجب دائمًا بصيغة JSON فقط."):
    """Generic AI response function for all modules."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1500
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return content
        
        return parsed
    except Exception as e:
        return {"error": str(e)}

def generate_scent_dna_analysis(profile_data, debug: bool = None):
    """تحليل DNA العطري - يحاول أولاً قاعدة المعرفة، ثم يعتمد على خبرة AI العامة"""
    
    query = f"{profile_data.get('gender', '')} {profile_data.get('personality_type', '')} {profile_data.get('favorite_notes', '')}"
    rag_context, rag_result = get_rag_context_for_ai(query, top_k=8, module_type='scent_dna', debug=debug)
    
    # محاولة أولى: استخدام قاعدة المعرفة (وضع صارم)
    if rag_result.is_valid and rag_result.notes and len(rag_result.notes) >= 3:
        available_notes_ar = [n.get('arabic', n.get('note', '')) for n in rag_result.notes if n.get('arabic') or n.get('note')]
        available_notes_en = [n.get('note', n.get('english', '')) for n in rag_result.notes if n.get('note') or n.get('english')]
        available_families = list(rag_result.families) if rag_result.families else []
        
        notes_list_ar = ', '.join(available_notes_ar)
        notes_list_en = ', '.join(available_notes_en)
        families_list = ', '.join(available_families)
        
        notes_details = []
        for n in rag_result.notes:
            detail = f"- {n.get('arabic', n.get('note', 'غير معروف'))} ({n.get('note', '')}) - عائلة: {n.get('family', 'غير محدد')}"
            if n.get('profile'):
                detail += f" - وصف: {n.get('profile')}"
            notes_details.append(detail)
        notes_details_text = '\n'.join(notes_details)
        
        prompt = f"""أنت خبير محلل عطور متخصص. مهمتك تقديم تحليل DNA عطري دقيق وشامل للمستخدم.

═══════════════════════════════════════════════════════════
📚 قاعدة المعرفة - المصدر الأساسي:
═══════════════════════════════════════════════════════════

📋 النوتات المتاحة (استخدم من هذه القائمة بالأولوية):
{notes_details_text}

📋 العائلات المتاحة:
{families_list}

═══════════════════════════════════════════════════════════
👤 بيانات المستخدم (اسس عليها التحليل):
═══════════════════════════════════════════════════════════
- الجنس: {profile_data.get('gender', 'غير محدد')}
- الفئة العمرية: {profile_data.get('age_range', 'غير محدد')}
- نوع الشخصية: {profile_data.get('personality_type', 'غير محدد')}
- النوتات المفضلة: {profile_data.get('favorite_notes', 'غير محدد')}
- النوتات المكروهة: {profile_data.get('disliked_notes', 'غير محدد')}
- المناخ: {profile_data.get('climate', 'غير محدد')}
- نوع البشرة: {profile_data.get('skin_type', 'غير محدد')}

═══════════════════════════════════════════════════════════
📋 متطلبات التحليل المفصل:
═══════════════════════════════════════════════════════════
اكتب تحليلاً متعمقاً وشاملاً يتضمن:
1. تعريف دقيق لشخصية المستخدم العطرية
2. شرح العلاقة بين البيانات الشخصية (الجنس، الشخصية، البشرة) والملف العطري
3. تبرير اختيار كل نوتة ولماذا تناسب المستخدم
4. تحليل كيمياء البشرة وتأثيرها على العطور
5. توصيات مفصلة حسب المناخ والمواسم
6. نقاط قوة الملف العطري وخصائصه المميزة
7. نصائح عملية للاستخدام الأمثل

قدم الإجابة بصيغة JSON مع تفاصيل شاملة:
{{
    "scent_personality": "اسم وصفي دقيق للشخصية العطرية",
    "personality_description": "وصف تفصيلي (3-5 جمل) يشرح الشخصية العطرية بعمق",
    "dna_characteristics": {{
        "primary_trait": "الخاصية الأساسية (مثل: الأنوثة الناعمة، الثقة الجريئة)",
        "secondary_traits": ["صفة 1", "صفة 2", "صفة 3"],
        "emotional_signature": "الصفة العاطفية للملف العطري",
        "intensity_level": "مستوى الشدة (خفيف/معتدل/قوي)"
    }},
    "recommended_families": ["عائلة 1 مع سبب الاختيار", "عائلة 2 مع سبب الاختيار"],
    "ideal_notes": {{
        "top_notes": ["نوتة 1 - السبب", "نوتة 2 - السبب"],
        "heart_notes": ["نوتة 1 - السبب", "نوتة 2 - السبب"],
        "base_notes": ["نوتة 1 - السبب", "نوتة 2 - السبب"]
    }},
    "notes_to_avoid": "نص واضح يصف النوتات التي يجب تجنبها مع الأسباب العلمية (مثال: يُفضل تجنب النوتة X لأن... و النوتة Y لأن...)",
    "skin_chemistry_analysis": "شرح تفصيلي لكيف ستتفاعل العطور مع بشرة المستخدم",
    "seasonal_recommendations": {{
        "spring": "توصيات الربيع المفصلة",
        "summer": "توصيات الصيف المفصلة",
        "fall": "توصيات الخريف المفصلة",
        "winter": "توصيات الشتاء المفصلة"
    }},
    "occasion_guide": {{
        "daily": "عطور اليوميات المناسبة",
        "work": "عطور العمل الاحترافية",
        "evening": "عطور السهرات الفاخرة",
        "special": "عطور المناسبات الخاصة"
    }},
    "fragrance_journey": "وصف رحلة العطر على البشرة (الفتح، الوسط، الختام)",
    "usage_tips": ["نصيحة 1 للاستخدام الأمثل", "نصيحة 2", "نصيحة 3"],
    "overall_analysis": "تحليل شامل وعميق (5-7 جمل) يربط كل العناصر السابقة"
}}"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""أنت محلل عطور متخصص. استخدم قاعدة المعرفة بالأولوية:
النوتات المتاحة: [{notes_list_ar}]
العائلات المتاحة: [{families_list}]

إذا لم تجد نوتة في القائمة، جرب بدائل من القائمة المتاحة. أجب بصيغة JSON فقط."""},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
            )
            
            content = response.choices[0].message.content
            parsed = parse_ai_response(content)
            
            if parsed is not None:
                validated = validate_ai_output(parsed, rag_result, 'scent_dna', strict=False)
                
                validated['_kb_notes_used'] = available_notes_ar
                validated['_kb_families_used'] = available_families
                validated['_kb_source'] = True
                
                if debug or DEBUG_MODE:
                    validated['_debug'] = rag_result.debug_info
                    validated['_mode'] = 'kb_primary'
                
                return validated
        except Exception as e:
            print(f"⚠️ KB Mode Error: {str(e)}")
    
    # خطة احتياطية: استخدام خبرة AI العامة (وضع خفيف)
    print("📌 الانتقال إلى وضع AI العام لعدم توفر بيانات كافية في قاعدة المعرفة")
    
    prompt_ai_mode = f"""أنت خبير عطور متخصص بخبرة عميقة. مهمتك تقديم تحليل Scent DNA شامل وعميق للمستخدم.

═══════════════════════════════════════════════════════════
👤 بيانات المستخدم (اسس عليها التحليل):
═══════════════════════════════════════════════════════════
- الجنس: {profile_data.get('gender', 'غير محدد')}
- الفئة العمرية: {profile_data.get('age_range', 'غير محدد')}
- نوع الشخصية: {profile_data.get('personality_type', 'غير محدد')}
- النوتات المفضلة: {profile_data.get('favorite_notes', 'غير محدد')}
- النوتات المكروهة: {profile_data.get('disliked_notes', 'غير محدد')}
- المناخ: {profile_data.get('climate', 'غير محدد')}
- نوع البشرة: {profile_data.get('skin_type', 'غير محدد')}

═══════════════════════════════════════════════════════════
📋 متطلبات التحليل المتقدم:
═══════════════════════════════════════════════════════════
اكتب تحليلاً متعمقاً وشاملاً يتضمن:
1. تعريف شامل وفريد للشخصية العطرية
2. تحليل العلاقة بين السمات الشخصية والملف العطري
3. تفسير علمي لاختيار كل عائلة ونوتة
4. تحليل تفصيلي لكيمياء البشرة وتأثيرها
5. توصيات مفصلة حسب جميع المواسم
6. دليل شامل للاستخدام حسب المناسبات
7. وصف رحلة العطر على البشرة
8. نصائح عملية احترافية

قدم الإجابة بصيغة JSON شاملة:
{{
    "scent_personality": "اسم وصفي دقيق وفريد للشخصية العطرية",
    "personality_description": "وصف تفصيلي (4-6 جمل) يكشف عمق الشخصية العطرية",
    "dna_characteristics": {{
        "primary_trait": "الخاصية الأساسية المميزة",
        "secondary_traits": ["صفة 1", "صفة 2", "صفة 3", "صفة 4"],
        "emotional_signature": "الطابع العاطفي الفريد للملف",
        "intensity_level": "مستوى الشدة الموصى به",
        "character_essence": "جوهر الشخصية في جملة واحدة"
    }},
    "recommended_families": [
        {{"family": "اسم العائلة", "reason": "السبب التفصيلي للتوصية", "intensity": "معتدل/قوي/خفيف"}}
    ],
    "ideal_notes": {{
        "top_notes": ["نوتة 1 - (السبب العلمي)", "نوتة 2 - (السبب العلمي)"],
        "heart_notes": ["نوتة 1 - (السبب العلمي)", "نوتة 2 - (السبب العلمي)"],
        "base_notes": ["نوتة 1 - (السبب العلمي)", "نوتة 2 - (السبب العلمي)"]
    }},
    "notes_to_avoid": "نص واضح ومفصل يصف النوتات التي يُفضل تجنبها مع الأسباب العلمية الدقيقة",
    "skin_chemistry_analysis": "تحليل متقدم لكيفية تفاعل العطور مع البشرة (تأثر بـ: نوع البشرة، الحموضة، الزيوت)",
    "seasonal_recommendations": {{
        "spring": "عطور الربيع المناسبة مع التفاصيل",
        "summer": "عطور الصيف الخفيفة مع النصائح",
        "fall": "عطور الخريف الدافئة مع الأسباب",
        "winter": "عطور الشتاء الفاخرة مع التوصيات"
    }},
    "occasion_guide": {{
        "daily": "خيارات يومية عملية ومريحة",
        "work": "عطور احترافية للعمل (محترمة، واثقة)",
        "evening": "عطور السهرات والحفلات (جريئة، رومانسية)",
        "special": "عطور المناسبات الخاصة (فاخرة، تأثيرية)"
    }},
    "fragrance_journey": "شرح تفصيلي لرحلة العطر: (الافتتاحية - الملاحظات العليا - التطور - الختام)",
    "performance_metrics": {{
        "longevity": "المدة المتوقعة (ساعات)",
        "sillage": "مدى الانتشار (خافت/متوسط/قوي)",
        "projection": "قوة التأثير"
    }},
    "usage_tips": [
        "نصيحة 1 للاستخدام الأمثل",
        "نصيحة 2 لتعزيز البقاء",
        "نصيحة 3 لتحسين التجربة",
        "نصيحة 4 احترافية"
    ],
    "complementary_products": "منتجات إضافية (مثل العطور الأخرى المتناسبة)",
    "overall_analysis": "تحليل شامل وعميق (6-8 جمل) يربط كل العناصر ويصف الملف العطري الفريد"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير عطور محترف بخبرة عميقة. قدم تحليل DNA عطري متقدم بناءً على بيانات المستخدم. أجب بصيغة JSON فقط."},
                {"role": "user", "content": prompt_ai_mode}
            ],
            max_completion_tokens=2000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is not None:
            parsed['_kb_source'] = False
            parsed['_mode'] = 'ai_general'
            
            if debug or DEBUG_MODE:
                parsed['_debug'] = {'source': 'AI General Knowledge', 'kb_insufficient': True}
            
            return parsed
        
        fallback = get_default_response('scent_dna')
        fallback['_mode'] = 'fallback_safe'
        return fallback
        
    except Exception as e:
        fallback = get_default_response('scent_dna')
        fallback['error'] = str(e)
        fallback['_mode'] = 'error_fallback'
        return fallback

def generate_custom_perfume(perfume_data, scent_profile=None, debug: bool = None):
    """تصميم عطر مخصص باستخدام RAG كمصدر وحيد للحقيقة"""
    
    profile_context = ""
    if scent_profile:
        profile_context = f"""
معلومات الملف العطري السابق:
- الشخصية العطرية: {scent_profile.scent_personality or 'غير محدد'}
- النوتات المفضلة: {scent_profile.favorite_notes or 'غير محدد'}
- النوتات المكروهة: {scent_profile.disliked_notes or 'غير محدد'}
"""
    
    query = f"{perfume_data.get('occasion', '')} {perfume_data.get('intensity', '')}"
    rag_context, rag_result = get_rag_context_for_ai(query, top_k=8, module_type='custom_perfume', debug=debug)
    
    if not rag_result.is_valid:
        fallback = get_default_response('custom_perfume')
        fallback['_rag_status'] = 'no_data'
        return fallback
    
    top_notes = [n.get('arabic', n.get('note', '')) for n in rag_result.notes if n.get('role', '').lower() == 'top']
    heart_notes = [n.get('arabic', n.get('note', '')) for n in rag_result.notes if n.get('role', '').lower() == 'heart']
    base_notes = [n.get('arabic', n.get('note', '')) for n in rag_result.notes if n.get('role', '').lower() == 'base']
    all_notes = [n.get('arabic', n.get('note', '')) for n in rag_result.notes]

    prompt = f"""أنت صانع عطور محترف (Perfumer). قم بتصميم عطر شخصي فريد بناءً على المتطلبات التالية:

{rag_context}

⚠️ قواعد صارمة - يجب الالتزام بها:
1. استخدم فقط النوتات العلوية المتاحة: {', '.join(top_notes) if top_notes else 'اختر من النوتات العامة'}
2. استخدم فقط النوتات الوسطى المتاحة: {', '.join(heart_notes) if heart_notes else 'اختر من النوتات العامة'}
3. استخدم فقط النوتات القاعدية المتاحة: {', '.join(base_notes) if base_notes else 'اختر من النوتات العامة'}
4. جميع النوتات المتاحة: {', '.join(all_notes)}
5. لا تذكر أي نوتة غير موجودة في القوائم أعلاه

متطلبات العطر:
- مناسبة الاستخدام: {perfume_data.get('occasion', 'يومي')}
- درجة الثبات المطلوبة: {perfume_data.get('intensity', 'متوسط')}
- الميزانية: {perfume_data.get('budget', 'متوسطة')}
{profile_context}

صمم عطرًا فريدًا وقدم الإجابة بصيغة JSON فقط:
{{
    "name": "اسم العطر المقترح (اسم إبداعي وجذاب)",
    "name_meaning": "معنى الاسم",
    "top_notes": ["نوتة علوية من القائمة المتاحة فقط"],
    "heart_notes": ["نوتة وسطى من القائمة المتاحة فقط"],
    "base_notes": ["نوتة قاعدية من القائمة المتاحة فقط"],
    "description": "وصف تسويقي جذاب للعطر في 3-4 جمل",
    "match_score": 92,
    "usage_recommendations": "توصيات الاستخدام المثالية",
    "longevity": "مدة الثبات المتوقعة",
    "sillage": "قوة الانتشار (خفيف/متوسط/قوي)",
    "best_seasons": ["الموسم 1", "الموسم 2"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت صانع عطور محترف. استخدم فقط النوتات المذكورة في السياق. لا تخترع أي نوتة جديدة. أجب بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return get_default_response('custom_perfume')
        
        validated = validate_ai_output(parsed, rag_result, 'custom_perfume', strict=False)
        
        if debug or DEBUG_MODE:
            validated['_debug'] = rag_result.debug_info
        
        return validated
        
    except Exception as e:
        fallback = get_default_response('custom_perfume')
        fallback['error'] = str(e)
        return fallback

def search_real_perfume_products(search_query, category="all", price_range="all", web_search_results=None):
    """Search for real perfume products from online stores using AI with web search data."""
    
    category_context = ""
    if category and category != "all":
        category_map = {
            "زيوت": "perfume oils and essential oils",
            "نوتات": "fragrance notes and raw materials",
            "عبوات": "perfume bottles and packaging",
            "عطور نسائية": "women's perfumes and fragrances",
            "عطور رجالية": "men's perfumes and colognes",
            "عطور يونيسكس": "unisex fragrances"
        }
        category_context = f"Focus on: {category_map.get(category, category)}"
    
    price_context = ""
    if price_range and price_range != "all":
        price_map = {
            "budget": "under $50 USD (budget-friendly options)",
            "mid": "between $50-$150 USD (mid-range)",
            "luxury": "above $150 USD (luxury and niche)"
        }
        price_context = f"Price range: {price_map.get(price_range, price_range)}"

    web_data_context = ""
    if web_search_results:
        web_data_context = f"""
REAL PRODUCT DATA FROM WEB SEARCH:
{web_search_results}

Extract ONLY products that appear in the search results above. Use the exact URLs, prices, and product names from the search data.
"""

    prompt = f"""You are a perfume shopping assistant. Based on the web search results provided, extract and structure real perfume products.

User is searching for: "{search_query}"
{category_context}
{price_context}
{web_data_context}

CRITICAL INSTRUCTIONS:
1. ONLY use products that appear in the web search results
2. Use EXACT URLs from the search results - do not modify or fabricate URLs
3. Use EXACT prices shown in the search results
4. If a product doesn't have a clear purchase URL, skip it

Return ONLY valid JSON with this structure:
{{
    "products": [
        {{
            "name": "Exact product name from search",
            "brand": "Brand name",
            "category": "Category in Arabic (زيوت/نوتات/عبوات/عطور نسائية/عطور رجالية/عطور يونيسكس)",
            "price": "$XX.XX (exact price from search)",
            "original_price": "$XX.XX or null",
            "concentration": "EDP/EDT/Parfum/Oil",
            "size": "50ml/100ml etc",
            "description": "Brief Arabic description",
            "main_notes": "Notes if available",
            "store_name": "Store name from URL",
            "store_url": "EXACT URL from search results",
            "rating": 4.5,
            "image_placeholder": "emoji"
        }}
    ],
    "search_summary": "Arabic summary of real results found",
    "data_source": "web_search"
}}

If no valid products found in search results, return empty products array."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a perfume product data extractor. Extract ONLY real products from the provided web search data. Never fabricate URLs or prices."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2500
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return {"products": [], "search_summary": "لم يتم العثور على نتائج", "data_source": "none"}
        
        return parsed
    except Exception as e:
        return {"products": [], "search_summary": f"حدث خطأ: {str(e)}", "error": str(e), "data_source": "error"}


def generate_recommendations(query, scent_profile=None, products=None):
    profile_context = ""
    if scent_profile:
        profile_context = f"""
معلومات الملف العطري السابق:
- الشخصية العطرية: {scent_profile.scent_personality or 'غير محدد'}
- النوتات المفضلة: {scent_profile.favorite_notes or 'غير محدد'}
- النوتات المكروهة: {scent_profile.disliked_notes or 'غير محدد'}
"""
    
    # 🔍 RAG Enhancement - Retrieve relevant notes from knowledge base
    rag_context, rag_result = get_rag_context_for_ai(query, top_k=10, module_type='recommendations')
    
    if not rag_result.is_valid:
        return get_default_response('recommendations')

    prompt = f"""أنت خبير عطور محترف ومحلّل روائح متخصص.

{rag_context}

مهمتك هي تحديد العطور التي تطابق وصف المستخدم بأعلى دقة ممكنة.
التركيز الأساسي: روح العطر (DNA) وليس مجرد تطابق النوتات.

معايير الاختيار الصارمة:
1. ركّز على DNA العطر: "لا تعتمد على مجرد تشابه النوتات. ركّز على الـDNA الحقيقي للعطر وأسلوبه العام وطابعه الرئيسي (مثل: بحري، بخوري، دخاني، فاكهي، بودري، نظيف…)."

2. عائلات العطور: "إذا كان الوصف بخوري–بحري فلا يُسمح باختيار عطور شرقية ثقيلة، ولا عطور بودرية، ولا عطور فاكهية–دخانية."

3. الأسلوب العام: "استبعد العطور التي تختلف في الأسلوب العام حتى لو تشابهت في بعض النوتات. الأسلوب أهم من المكونات."

4. التطابق مع 6 عوامل أساسية (لا تعتمد عنصراً واحداً فقط):
   أ) النوتات (Top/Heart/Base)
   ب) العائلة العطرية
   ج) الأسلوب العام (بحري، حار، ناعم، حاد، بخوري، إلخ)
   د) الطابع والشخصية (رسمي، شبابي، فاخر، رومانسي، رياضي، إلخ)
   هـ) قوة الفوحان والثبات
   و) المزاج الكلي والأجواء المناسبة

5. التطابق الكامل: "لا تُظهر أي عطر لا يتوافق مع: نوع الاستخدام + مزاج العطر + الأجواء المناسبة + شخصية العطر."

6. الجو العام: "أي عطر لا يطابق الجو العام للوصف (النظافة – البخور – النضارة – الرسمية – الأناقة) يجب استبعاده فورًا."

7. تصحيح الانحياز: "لا تقم باختيار عطور niche أو عطور فاخرة جداً إلا إذا كان الوصف يشير صراحة إلى ذلك. التزم بالعائلة والمنطق قبل الشهرة."

8. نسب التطابق: "إذا لم تكن نسبة التطابق عالية جداً (أقل من 80%) فلا تضع العطر في المركز الأول."
9. "يجب ربط الوصف بالعائلة العطرية الدقيقة مثل (Aromatic Aquatic Incense) وليس العائلة العامة فقط مثل Woody أو Fresh. أي اختلاف في العائلة الدقيقة يعني استبعاد العطر مباشرة."
10. "يجب مطابقة الطابع العمري والذكوري/الرسمي للعطر. إذا كان الوصف ناضجًا، رسميًا، فاخرًا، فلا يُسمح باختيار عطر شبابي أو حلو أو فاكهي أو بودري."
11."إذا ذكر المستخدم كلمة (بخور أو Incense) فلا يُسمح باختيار عطر لا يحتوي رسميًا على نوتة البخور ضمن مكوناته الأساسية."
خطوات العمل:
1) استخرج من الوصف:
   - النوتات (إن وجدت)
   - العائلة المطلوبة
   - الأسلوب والطابع
   - نوع الاستخدام
   - المزاج والأجواء
   - الجو العام (النظافة، البخور، الدفء، البرودة، إلخ)

2) قارن بـ 6 عوامل (ليس نوتة واحدة):
   - هل العائلة تطابق؟
   - هل الأسلوب يطابق؟
   - هل الطابع يطابق؟
   - هل الاستخدام يطابق؟
   - هل المزاج يطابق؟
   - هل النوتات تدعم بقية العوامل؟

3) اختر 3 عطور فقط بنسبة تطابق عالية جداً (85% فأعلى للمركز الأول):
   - اشرح التطابق بناءً على 6 عوامل
   - أظهر النوتات الفعلية
   - اشرح لماذا يطابق الـ DNA

4) استبعد بوضوح:
   - عطور من عائلات مختلفة
   - عطور بأسلوب عام مختلف
   - عطور لا تتطابق مع الاستخدام/المزاج
   - عطور niche بدون إشارة واضحة
   - عطور بنسبة تطابق منخفضة

وصف المستخدم:
"{query}"
{profile_context}

قدم الإجابة بصيغة JSON فقط:
{{
    "scent_analysis": {{
        "top_notes_requested": ["نوتة 1", "نوتة 2"],
        "heart_notes_requested": ["نوتة 1", "نوتة 2"],
        "base_notes_requested": ["نوتة 1", "نوتة 2"],
        "fragrance_family": "العائلة العطرية المطلوبة",
        "fragrance_style": "الأسلوب (بحري، بخوري، دخاني، ناعم، إلخ)",
        "fragrance_character": "الطابع (رسمي، شبابي، فاخر، رومانسي، إلخ)",
        "usage_type": "نوع الاستخدام (يومي، مساء، مناسبات، إلخ)",
        "mood_keywords": ["كلمة مفتاحية 1", "كلمة مفتاحية 2"],
        "overall_atmosphere": "الجو العام (نظيف، دافئ، بارد، برّاق، إلخ)",
        "intensity_required": "خفيف/متوسط/قوي"
    }},
    "top_3_matches": [
        {{
            "rank": 1,
            "name": "اسم العطر الكامل",
            "brand": "العلامة التجارية",
            "match_percentage": 92,
            "dna_alignment": "شرح كيف يطابق DNA العطر (الأسلوب والطابع)",
            "six_factor_analysis": {{
                "notes_match": "درجة تطابق النوتات مع شرح",
                "family_match": "هل العائلة تطابق؟",
                "style_match": "هل الأسلوب متطابق؟",
                "character_match": "هل الطابع متطابق؟",
                "sillage_match": "هل قوة الفوحان متطابقة؟",
                "mood_match": "هل المزاج متطابق؟"
            }},
            "actual_notes": {{
                "top": ["نوتة 1", "نوتة 2"],
                "heart": ["نوتة 1", "نوتة 2"],
                "base": ["نوتة 1", "نوتة 2"]
            }},
            "detailed_match_reason": "شرح شامل: كيف يطابق هذا العطر DNA المطلوب؟ لماذا؟",
            "best_for": "الاستخدام الأمثل",
            "sillage": "قوة الانتشار",
            "character_type": "نوع الطابع"
        }}
    ],
    "excluded_fragrances": [
        {{
            "name": "اسم العطر",
            "brand": "العلامة التجارية",
            "exclusion_reason": "سبب واضح: نوع عدم التطابق (مثال: عائلة مختلفة تماماً، أسلوب عام مختلف، استخدام غير متطابق، طابع غير مناسب)"
        }}
    ],
    "scientific_conclusion": "ملخص علمي شامل: DNA المطلوب مقابل ما اخترناه",
    "dna_summary": "ملخص DNA العطر الأساسي المطلوب",
    "additional_advice": "نصيحة إضافية للمستخدم"
}}"""

    default_response = {
        "scent_analysis": {
            "top_notes_requested": ["برغموت", "ليمون"],
            "heart_notes_requested": ["فلفل", "نعناع"],
            "base_notes_requested": ["عنبر", "مسك"],
            "fragrance_family": "شرقي-عطري",
            "fragrance_style": "دافئ وحاد",
            "fragrance_character": "رسمي وعصري",
            "usage_type": "يومي ومساء",
            "mood_keywords": ["عصري", "جذاب"],
            "overall_atmosphere": "دافئ وفاخر",
            "intensity_required": "متوسط"
        },
        "top_3_matches": [
            {
                "rank": 1,
                "name": "Dior Sauvage EDP",
                "brand": "Dior",
                "match_percentage": 90,
                "dna_alignment": "DNA مطابق تماماً: عطر دافئ وحاد مع أسلوب عصري وطابع رسمي",
                "six_factor_analysis": {
                    "notes_match": "✓ برغموت وفلفل مطابق تماماً مع قاعدة عنبرية دافئة",
                    "family_match": "✓ عائلة شرقية-عطرية متطابقة تماماً",
                    "style_match": "✓ أسلوب دافئ وحاد متطابق",
                    "character_match": "✓ طابع رسمي وعصري متطابق",
                    "sillage_match": "✓ فوحان متوسط إلى قوي مطابق",
                    "mood_match": "✓ مزاج عصري وجذاب متطابق"
                },
                "actual_notes": {
                    "top": ["برغموت أمبروكسادي", "ليمون"],
                    "heart": ["فلفل سيشيلي"],
                    "base": ["عنبر جراي", "مسك"]
                },
                "detailed_match_reason": "DNA مثالي: يطابق جميع 6 عوامل. البرغموت والفلفل المطلوبان يجتمعان مع قاعدة عنبرية دافئة. الأسلوب دافئ وحاد والطابع رسمي وعصري. مناسب للاستخدام اليومي والمساء",
                "best_for": "الاستخدام اليومي والمناسبات والعمل",
                "sillage": "متوسط إلى قوي",
                "character_type": "رسمي وعصري"
            },
            {
                "rank": 2,
                "name": "Spicebomb Extreme by Viktor & Rolf",
                "brand": "Viktor & Rolf",
                "match_percentage": 84,
                "dna_alignment": "DNA متطابق: عطر دافئ وحاد مع طابع رسمي",
                "six_factor_analysis": {
                    "notes_match": "✓ فلفل أسود وبهارات دافئة مع عنبر قوي",
                    "family_match": "✓ عائلة شرقية دافئة متطابقة",
                    "style_match": "✓ أسلوب دافئ وحاد مطابق",
                    "character_match": "✓ طابع رسمي وفاخر متطابق",
                    "sillage_match": "✓ فوحان قوي جداً مطابق",
                    "mood_match": "~ مزاج فاخر أكثر من عصري"
                },
                "actual_notes": {
                    "top": ["بهارات", "تفاح"],
                    "heart": ["فلفل أسود", "قرنفل", "ميرة"],
                    "base": ["عنبر", "خشب، عود"]
                },
                "detailed_match_reason": "DNA متطابق في معظم العوامل: البهارات والفلفل الأسود يوفران الدفء والحدة. القاعدة العنبرية قوية جداً. الأسلوب دافئ والطابع رسمي. الفرق الوحيد: أكثر فخامة وأقل عصرية قليلاً",
                "best_for": "المساء والمناسبات الخاصة والعمل الرسمي",
                "sillage": "قوي جداً",
                "character_type": "رسمي وفاخر"
            },
            {
                "rank": 3,
                "name": "Givenchy Gentleman Reserve Privée",
                "brand": "Givenchy",
                "match_percentage": 79,
                "dna_alignment": "DNA متطابق جزئياً: عطر دافئ مع طابع رسمي",
                "six_factor_analysis": {
                    "notes_match": "~ برغموت وفلفل لكن مع لمسات خشبية أكثر",
                    "family_match": "✓ عائلة عطرية-خشبية متطابقة",
                    "style_match": "✓ أسلوب دافئ متطابق",
                    "character_match": "✓ طابع رسمي متطابق",
                    "sillage_match": "~ فوحان متوسط (أقل قليلاً من المطلوب)",
                    "mood_match": "✓ مزاج رسمي وعصري متطابق"
                },
                "actual_notes": {
                    "top": ["برغموت", "ليمون"],
                    "heart": ["فلفل، زنجبيل"],
                    "base": ["خشب الأرز", "مسك، عنبر"]
                },
                "detailed_match_reason": "DNA متطابق في الأساس لكن مع اختلاف طفيف: البرغموت والفلفل موجودان لكن مع لمسات خشبية أقوى. الأسلوب دافئ والطابع رسمي. الفوحان قليل أقل من المطلوب",
                "best_for": "العمل الرسمي والمناسبات والاستخدام اليومي",
                "sillage": "متوسط",
                "character_type": "رسمي وكلاسيكي"
            }
        ],
        "excluded_fragrances": [
            {
                "name": "Acqua di Gio",
                "brand": "Giorgio Armani",
                "exclusion_reason": "DNA مختلف تماماً: عائلة مائية-نظيفة بدل شرقية-عطرية. أسلوب بارد ومنعش بدل دافئ وحاد. لا يطابق طابع الوصف"
            },
            {
                "name": "Light Blue",
                "brand": "Dolce & Gabbana",
                "exclusion_reason": "DNA غير متطابق: عطر حمضي خفيف بدل دافئ وحاد. الأسلوب نظيف وبارد. لا يناسب الاستخدام المطلوب"
            },
            {
                "name": "Aventus",
                "brand": "Creed",
                "exclusion_reason": "عائلة فاكهية-حارة بدل شرقية-عطرية. الأسلوب مختلف (فاكهي) وليس دافئ-حاد. تصنيف niche فاخر جداً بدون إشارة صريحة"
            }
        ],
        "dna_summary": "العطر المطلوب: شرقي-عطري دافئ وحاد برغموت وفلفل وعنبر دافئ. طابع رسمي وعصري. استخدام يومي ومساء",
        "scientific_conclusion": "الوصف يطلب عطراً متوازناً بين الدفء والحدة، بأسلوب عصري ورسمي. التركيز على DNA العطر (الأسلوب والطابع) أهم من النوتات وحدها",
        "additional_advice": "اختر بناءً على DNA العطر وليس النوتات فقط. تأكد من تطابق الأسلوب والطابع مع احتياجاتك قبل الشراء"
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير عطور محترف ومحلّل روائح متخصص. قدم تحليلات دقيقة بناءً على DNA العطر (الأسلوب والطابع) وليس النوتات فقط. قارن دائماً بـ 6 عوامل: النوتات، العائلة، الأسلوب، الطابع، الفوحان، المزاج. استبعد العطور من عائلات مختلفة وأساليب مختلفة. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2500
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return default_response
        
        if 'top_3_matches' not in parsed or not isinstance(parsed.get('top_3_matches'), list):
            return default_response
        
        return parsed
    except Exception as e:
        default_response["error"] = str(e)
        return default_response

SERVICES_MAP = {
    'bio_scent': {'name_ar': 'تحليل الرائحة الحيوية', 'keywords': ['حيوي', 'صوت', 'جلد', 'مزاج', 'طاقة']},
    'skin_chemistry': {'name_ar': 'كيمياء البشرة', 'keywords': ['بشرة', 'كيمياء', 'حساسية', 'درجة حرارة']},
    'temp_volatility': {'name_ar': 'التطاير الحراري', 'keywords': ['حرارة', 'تطاير', 'ثبات', 'انتشار']},
    'metabolism': {'name_ar': 'التمثيل الغذائي', 'keywords': ['أيض', 'تمثيل', 'طاقة', 'حركة']},
    'climate': {'name_ar': 'محرك المناخ', 'keywords': ['مناخ', 'حار', 'بارد', 'رطب', 'صحراوي']},
    'neuroscience': {'name_ar': 'علم الأعصاب العطري', 'keywords': ['دماغ', 'ذاكرة', 'عاطفة', 'نفسي']},
    'stability': {'name_ar': 'الثبات والانتشار', 'keywords': ['ثبات', 'دوام', 'انتشار', 'طول']},
    'predictive': {'name_ar': 'الذكاء التنبّؤي', 'keywords': ['تنبؤ', 'توقع', 'مستقبل', 'نمط']},
    'scent_personality': {'name_ar': 'الشخصية العطرية', 'keywords': ['شخصية', 'نمط', 'طباع', 'هوية']},
    'signature': {'name_ar': 'العطر التوقيعي', 'keywords': ['توقيع', 'فريد', 'خاص', 'شهرة']},
    'occasion': {'name_ar': 'عطر لكل مناسبة', 'keywords': ['مناسبة', 'حفل', 'عمل', 'يومي', 'سهرة']},
    'habit_planner': {'name_ar': 'الخطة العطرية', 'keywords': ['خطة', 'روتين', 'عادة', 'جدول']},
    'digital_twin': {'name_ar': 'التوأم الرقمي', 'keywords': ['رقمي', 'افتراضي', 'نموذج', 'محاكاة']},
    'adaptive': {'name_ar': 'العطر التكيّفي', 'keywords': ['تكيف', 'تغير', 'ديناميكي', 'مرن']},
    'oil_mixer': {'name_ar': 'مازج الزيوت', 'keywords': ['خلط', 'زيوت', 'نوتات', 'تركيب']},
    'scent_dna': {'name_ar': 'بصمة الرائحة', 'keywords': ['DNA', 'بصمة', 'فريد', 'أصل']},
    'custom_perfume': {'name_ar': 'تصميم عطر مخصص', 'keywords': ['تصميم', 'مخصص', 'إنشاء', 'صياغة']},
    'recommendations': {'name_ar': 'توصيات العطور', 'keywords': ['توصية', 'اقتراح', 'اختيار', 'تطابق']},
    'blend_predictor': {'name_ar': 'الخلط التنبؤي', 'keywords': ['خلط', 'تنبؤ', 'نتيجة', 'توازن']},
}

def detect_article_services(title, summary, content, keywords):
    """اكتشاف الخدمات المناسبة من محتوى المقال"""
    try:
        prompt = f"""
        أنت خبير متخصص في تحليل محتوى العطور وربطه بالخدمات المناسبة.
        
        حلل المقال التالي واقترح جميع الخدمات المرتبطة والمناسبة:
        
        العنوان: {title}
        الملخص: {summary}
        الكلمات المفتاحية: {keywords}
        جزء من المحتوى: {content[:1000]}
        
        الخدمات المتاحة (19 خدمة):
        1. bio_scent - تحليل الرائحة الحيوية
        2. skin_chemistry - كيمياء البشرة
        3. temp_volatility - التطاير الحراري
        4. metabolism - التمثيل الغذائي
        5. climate - محرك المناخ
        6. neuroscience - علم الأعصاب العطري
        7. stability - الثبات والانتشار
        8. predictive - الذكاء التنبّؤي
        9. scent_personality - الشخصية العطرية
        10. signature - العطر التوقيعي
        11. occasion - عطر لكل مناسبة
        12. habit_planner - الخطة العطرية
        13. digital_twin - التوأم الرقمي
        14. adaptive - العطر التكيّفي
        15. oil_mixer - مازج الزيوت
        16. scent_dna - بصمة الرائحة
        17. custom_perfume - تصميم عطر مخصص
        18. recommendations - توصيات العطور
        19. blend_predictor - الخلط التنبؤي
        
        اقترح 4-7 خدمات الأنسب بناءً على:
        - محتوى وموضوع المقال
        - الكلمات المفتاحية والسياق
        - الصلة المباشرة والغير مباشرة
        - فائدة المستخدم
        
        أجب بصيغة JSON فقط:
        {{
            "services": ["key1", "key2", "key3", "key4"],
            "reasons": ["السبب 1", "السبب 2", "السبب 3", "السبب 4"]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت محلل محتوى متخصص في مجال العطور والروائح. اكتشف جميع الخدمات المرتبطة بالمقال بناءً على سياقه ومحتواه. أرجع 4-7 خدمات مناسبة. أجب بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=800
        )
        
        content_response = response.choices[0].message.content
        parsed = parse_ai_response(content_response)
        
        if parsed and 'services' in parsed:
            services = parsed.get('services', [])
            # تصفية الخدمات من التكرار والتأكد من أنها موجودة
            valid_services = [s for s in services if s in SERVICES_MAP]
            return valid_services[:7]  # أقصى 7 خدمات
        return []
    except Exception as e:
        print(f"Service detection error: {str(e)}")
        return []

def generate_article(topic, keywords, tone, language='ar'):
    """Generate a professionally formatted article using AI"""
    
    # 🔍 RAG Enhancement - Retrieve relevant notes for article
    rag_context, rag_result = get_rag_context_for_ai(f"{topic} {keywords}", top_k=5, module_type='article')
    
    if not rag_result.is_valid:
        rag_context = ""
    
    prompt = f"""
    أنت محرر ومؤلف محتوى محترف متخصص في مجال العطور والروائح.
    
{rag_context if rag_context else "⚠️ لا توجد نوتات مسترجعة - قدم محتوى تعليمي عام بدون أسماء عطور محددة."}
    
    قم بإنشاء مقال شامل واحترافي حول الموضوع التالي:
    الموضوع: {topic}
    الكلمات المفتاحية: {keywords}
    النبرة: {tone}
    
    ⚠️ تنسيق المحتوى مهم جداً - يجب أن يكون بصيغة HTML احترافية:
    
    المتطلبات الإلزامية للمحتوى:
    1. عنوان رئيسي جذاب وإبداعي
    2. ملخص احترافي (150-200 كلمة)
    3. فهرس محتويات (Table of Contents) مع روابط داخلية
    4. 4-6 عناوين فرعية رئيسية (H2) مع محتوى غني تحت كل عنوان
    5. عناوين فرعية ثانوية (H3) حسب الحاجة
    6. اقتباسات ملهمة من خبراء العطور (2-3 اقتباسات على الأقل)
    7. قوائم نقطية وترقيمية حيث يناسب
    8. نصائح عملية في boxes مميزة
    9. قسم المراجع والمصادر (3-5 مراجع) تكون مراجع حقيقية وليس كمثال
    10. خاتمة قوية مع دعوة للعمل
    
    صيغة HTML المطلوبة للمحتوى:
    - استخدم <h2 id="section-X"> للعناوين الرئيسية (مع ID للفهرس)
    - استخدم <h3> للعناوين الفرعية
    - استخدم <blockquote class="quote-box"> للاقتباسات
    - استخدم <div class="tip-box"> للنصائح المميزة
    - استخدم <div class="reference-box"> للمراجع
    - استخدم <ul> و <ol> للقوائم
    - استخدم <strong> و <em> للتأكيد
    - استخدم <a href="#section-X"> للروابط الداخلية في الفهرس
    - استخدم <a href="URL" target="_blank" rel="noopener"> للروابط الخارجية
    شروط مهمة :
    - يجب تضمين الكلمة المفتاحية الأساسية في أول 150 كلمة من المقال.
    - يجب تضمين الكلمة المفتاحية في 30% من عناوين H2.
    - يجب توزيع الكلمة المفتاحية في النص بنسبة 1% إلى 1.5% من إجمالي عدد الكلمات.
    - يجب تضمين كلمات LSI مرتبطة بالموضوع مثل الروائح، الفوحان، الثبات، نوتات العطر، العائلة العطرية، إلخ.
    -إنتاج Meta Description داخل JSON "meta_description": 
    "وصف موجز 150 حرفاً يظهر في نتائج البحث"
    - إنتاج Slug تلقائي للمقال "slug": "عنوان-متوافق-مع-seo-بالإنجليزية-ومنفصل-بشرطة"
    - إدراج Structured Data Schema Article داخل json 
    "schema": "<script     type='application/ld+json'>...</script>"
    - يجب أن يكون المحتوى فريد بنسبة 100% وغير معاد من أي مقالة أخرى.
    - لا تستخدم قوالب ثابتة أو جمل مكررة بين المقالات المختلفة.
    - استخدم أسلوباً بشرياً سلساً.
    - تجنب التكرار والحشو.
    - استخدم أمثلة واقعية وتفسيرات مبسطة.
    - استخدم انتقالات لغوية طبيعية بين الفقرات.
    - يجب أن تحتوي كل فقرة على 50–130 كلمة.
    - لا تكتب فقرات طويلة جداً أو جمل قصيرة جداً.
    - يجب إضافة رابطين خارجيين على الأقل لمواقع موثوقة: Fragrantica, Basenotes.
    - يجب الحفاظ على النبرة التي يحددها المستخدم: رسمية، عاطفية، تقنية، تسويقية، إلخ.
    - لا تخرج عن النبرة إطلاقاً.
    -إضافة قواعد E-E-A-T الخاصة بجوجل
    - تضمين معلومات خبراء العطور.
    - تضمين جمل تظهر الخبرة والمعرفة (Experience).
    - إظهار تحليل متخصص ومتعمق.
    - يجب أن تكون جميع الروابط والمراجع حقيقية من مواقع معروفة مثل:
    - https://www.fragrantica.com
    - https://www.basenotes.com
    - https://www.perfumerflavorist.com
    -إضافة خاصية Outbound SEO Safety
    - لا تضع روابط لمواقع غير موثوقة.
    - لا تضع روابط عشوائية أو غير موجودة.


    مثال على بنية المحتوى:
    <nav class="toc-box">
        <h4>📑 فهرس المحتويات</h4>
        <ol>
            <li><a href="#section-1">العنوان الأول</a></li>
            <li><a href="#section-2">العنوان الثاني</a></li>
        </ol>
    </nav>
    
    <h2 id="section-1">العنوان الأول</h2>
    <p>المحتوى...</p>
    
    <blockquote class="quote-box">
        <p>"الاقتباس هنا"</p>
        <cite>- اسم الخبير</cite>
    </blockquote>
    
    <div class="tip-box">
        <strong>💡 نصيحة:</strong> النصيحة هنا
    </div>
    
    <div class="reference-box">
        <h4>📚 المراجع والمصادر</h4>
        <ol>
            <li>اسم المرجع - <a href="URL" target="_blank">رابط</a></li>
        </ol>
    </div>
    
    أجب بصيغة JSON فقط:
    {{
        "title": "العنوان الرئيسي الجذاب",
        "summary": "ملخص احترافي شامل 150-200 كلمة",
        "content": "المحتوى الكامل بصيغة HTML المنسقة (2000-3000 كلمة)",
        "keywords": "كلمات مفتاحية مفصولة بفواصل"
    }}
    """
    
    # Default article response for fallback
    default_article = {
        "success": True,
        "title": f"{topic} - دليل شامل",
        "summary": f"دليل احترافي شامل عن {topic} يغطي جميع الجوانب المهمة والمتعلقة بعالم العطور والروائح.",
        "content": f"""<nav class="toc-box">
    <h4>📑 فهرس المحتويات</h4>
    <ol>
        <li><a href="#section-1">مقدمة عن {topic}</a></li>
        <li><a href="#section-2">الخصائص الرئيسية</a></li>
        <li><a href="#section-3">الفوائد والاستخدامات</a></li>
        <li><a href="#section-4">نصائح عملية</a></li>
    </ol>
</nav>

<h2 id="section-1">مقدمة عن {topic}</h2>
<p>{topic} يمثل جزءاً مهماً من عالم العطور والروائح. يتطلب فهماً عميقاً للعوامل المختلفة المؤثرة على اختيار العطور المناسبة.</p>

<h2 id="section-2">الخصائص الرئيسية</h2>
<ul>
    <li>جودة عالية ومعايير صارمة في الاختيار</li>
    <li>توافق مع أنواع مختلفة من البشرة</li>
    <li>ثبات طويل الأمد وفوحان متوازن</li>
    <li>تركيبة متقنة تجمع بين النوتات المختلفة</li>
</ul>

<h2 id="section-3">الفوائد والاستخدامات</h2>
<div class="tip-box">
    <strong>💡 نصيحة:</strong> اختر العطر الذي يناسب شخصيتك وينعكس على أسلوبك الخاص.
</div>
<p>يمكن استخدام {topic} في مختلف المناسبات والأوقات، مما يجعله خياراً متعدد الاستخدامات.</p>

<h2 id="section-4">نصائح عملية</h2>
<ol>
    <li>اختبر العطر على بشرتك قبل الشراء</li>
    <li>ضع العطر على نقاط الضغط (المعصمان، الرقبة، خلف الأذنين)</li>
    <li>لا تفرك معصميك معاً - دع العطر يجف بشكل طبيعي</li>
    <li>حافظ على العطر في مكان بارد وجاف بعيداً عن الضوء المباشر</li>
</ol>

<div class="reference-box">
    <h4>📚 المراجع والمصادر</h4>
    <ol>
        <li><a href="https://www.fragrantica.com" target="_blank" rel="noopener">Fragrantica - قاموس العطور العالمي</a></li>
        <li><a href="https://www.basenotes.com" target="_blank" rel="noopener">Basenotes - مجتمع محترفي العطور</a></li>
    </ol>
</div>""",
        "keywords": keywords,
        "suggested_services": []
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت كاتب محتوى محترف متخصص في مجال العطور. أنتج محتوى عالي الجودة ومنسق بشكل احترافي مع HTML صحيح. أجب بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            # استخدام المقال الافتراضي كبديل
            suggested_services = detect_article_services(default_article["title"], default_article["summary"], default_article["content"], keywords)
            default_article["suggested_services"] = suggested_services
            return default_article
        
        title = parsed.get('title', f'مقال عن {topic}')
        summary = parsed.get('summary', '')
        content = parsed.get('content', '')
        article_keywords = parsed.get('keywords', keywords)
        
        # اكتشاف الخدمات المناسبة
        suggested_services = detect_article_services(title, summary, content, article_keywords)
        
        return {
            "success": True,
            "title": title,
            "summary": summary,
            "content": content,
            "keywords": article_keywords,
            "suggested_services": suggested_services
        }
    
    except Exception as e:
        # في حالة حدوث خطأ، استخدام المقال الافتراضي
        print(f"Article generation error: {str(e)}")
        return default_article


def analyze_face_for_perfume(image_data, debug: bool = None):
    """
    Analyze face image using OpenAI Vision to recommend perfumes.
    """
    # 🔍 RAG Enhancement - Retrieve notes for face analysis
    rag_context, rag_result = get_rag_context_for_ai("شخصية أنيقة رسمية فاخرة", top_k=6, module_type='face_analyzer', debug=debug)
    
    if not rag_result.is_valid:
        return get_default_response('face_analyzer')
    
    prompt = f"""أنت خبير متخصص في تحليل الوجه واختيار العطور المناسبة. قم بتحليل هذه الصورة بدقة عالية واستخرج:

{rag_context}

1. **تحليل البشرة**:
   - نوع البشرة (جافة - دهنية - مختلطة - حساسة - عادية)
   - درجة لون البشرة (فاتحة جداً - فاتحة - متوسطة - حنطية - داكنة - داكنة جداً)
   - العمر التقريبي (18-25, 25-35, 35-45, 45-55, 55+)
   - تأثير البشرة على ثبات العطر
   - أفضل تركيز عطري (EDT, EDP, Parfum)
   - ثبات متوقع للعطر على هذه البشرة

2. **تحليل الشخصية من الملامح**:
   - الشخصية العامة (رسمي - واثق - رومانسي - هادئ - جريء - مغامر - أنيق)
   - الانطباع (قوي - أنيق - جذاب - خفيف - غامض - ودود)
   - المزاج (جريء - رومانسي - هادئ - مرح - جدي)
   - الـ Vibe (رياضي - رسمي - فخم - شبابي - كلاسيكي)
   - الأسلوب (Minimal - Bold - Elegant - Casual - Sophisticated)

3. **العائلات العطرية الأنسب** (اختر 3-5 من):
   Fresh Citrus, Woody Amber, Floral, Oriental, Aromatic, Leather, Aquatic, Gourmand, Oud, Musk

4. **أفضل 5 عطور** لهذا الشخص:
   لكل عطر قدم:
   - اسم العطر والعلامة التجارية
   - نسبة التوافق (0-100%)
   - لماذا يناسب هذا الشخص
   - نقاط قوة العطر
   - أين يُستخدم (يومي، عمل، مساء، مناسبات)

5. **عطر التوقيع** (Signature Perfume):
   - اسم العطر المثالي
   - سبب كونه الأنسب لهذا الشخص

6. **توصيات حسب المناسبة**:
   - يومي
   - عمل
   - مساء
   - مناسبات خاصة

أجب بصيغة JSON فقط:
{
    "skin_analysis": {
        "skin_type": "نوع البشرة",
        "skin_tone": "درجة اللون",
        "age_range": "الفئة العمرية",
        "perfume_effect": "تأثير البشرة على العطر",
        "best_concentration": "أفضل تركيز",
        "longevity_estimate": "ثبات متوقع بالساعات"
    },
    "personality_analysis": {
        "personality": "الشخصية",
        "impression": "الانطباع",
        "mood": "المزاج",
        "vibe": "الـ Vibe",
        "style": "الأسلوب"
    },
    "best_families": ["العائلة1", "العائلة2", "العائلة3"],
    "recommended_perfumes": [
        {
            "name": "اسم العطر",
            "brand": "العلامة",
            "match_score": 95,
            "why_suitable": "لماذا يناسب",
            "strengths": "نقاط القوة",
            "usage": "أين يُستخدم"
        }
    ],
    "signature_perfume": {
        "name": "اسم العطر التوقيعي",
        "reason": "سبب التوصية"
    },
    "occasion_recommendations": {
        "daily": "عطر يومي",
        "work": "عطر العمل",
        "evening": "عطر المساء",
        "special": "عطر المناسبات"
    }
}"""

    default_response = {
        "skin_analysis": {
            "skin_type": "مختلطة",
            "skin_tone": "متوسطة",
            "age_range": "25-35",
            "perfume_effect": "ثبات متوسط إلى جيد",
            "best_concentration": "EDP",
            "longevity_estimate": "6-8 ساعات"
        },
        "personality_analysis": {
            "personality": "أنيق وواثق",
            "impression": "جذاب",
            "mood": "هادئ",
            "vibe": "فخم",
            "style": "Elegant"
        },
        "best_families": ["Woody Amber", "Oriental", "Aromatic"],
        "recommended_perfumes": [
            {
                "name": "Dior Sauvage EDP",
                "brand": "Dior",
                "match_score": 92,
                "why_suitable": "يعكس الأناقة والثقة بالنفس",
                "strengths": "ثبات ممتاز، فوحان قوي، مناسب لجميع المواسم",
                "usage": "يومي وعمل"
            },
            {
                "name": "Bleu de Chanel",
                "brand": "Chanel",
                "match_score": 90,
                "why_suitable": "يناسب الشخصية الأنيقة والعصرية",
                "strengths": "متوازن، راقي، متعدد الاستخدامات",
                "usage": "يومي ومساء"
            },
            {
                "name": "Tom Ford Oud Wood",
                "brand": "Tom Ford",
                "match_score": 88,
                "why_suitable": "يعكس الفخامة والتميز",
                "strengths": "فريد، فخم، انطباع قوي",
                "usage": "مساء ومناسبات"
            },
            {
                "name": "Versace Pour Homme",
                "brand": "Versace",
                "match_score": 85,
                "why_suitable": "منعش وأنيق للاستخدام اليومي",
                "strengths": "خفيف، منعش، مريح",
                "usage": "يومي"
            },
            {
                "name": "Creed Aventus",
                "brand": "Creed",
                "match_score": 95,
                "why_suitable": "الاختيار الأمثل للشخصية القيادية",
                "strengths": "فاخر، مميز، ثبات استثنائي",
                "usage": "مناسبات خاصة"
            }
        ],
        "signature_perfume": {
            "name": "Creed Aventus",
            "reason": "يعكس شخصيتك القيادية وذوقك الرفيع، ويترك انطباعاً لا يُنسى"
        },
        "occasion_recommendations": {
            "daily": "Versace Pour Homme",
            "work": "Bleu de Chanel",
            "evening": "Tom Ford Oud Wood",
            "special": "Creed Aventus"
        }
    }

    try:
        if not image_data or not image_data.startswith('data:image'):
            return default_response
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "أنت خبير متخصص في تحليل الوجه واختيار العطور. حلل الصورة بدقة وأجب بصيغة JSON فقط."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data}
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed and 'skin_analysis' in parsed:
            return parsed
        else:
            return default_response
            
    except Exception as e:
        print(f"Face analysis error: {str(e)}")
        return default_response


def analyze_perfume_notes_bulk_import(text: str) -> dict:
    """
    تحليل نص يحتوي على نوتات عطرية واستخراج البيانات المنسقة
    Returns: {
        'success': bool,
        'notes': [{'name_en': str, 'name_ar': str, 'family': str, 'role': str, ...}],
        'error': str (if any)
    }
    """
    if not text or not text.strip():
        return {'success': False, 'error': 'يجب إدخال نص يحتوي على النوتات'}
    
    prompt = f"""أنت متخصص عالمي في العطور والنوتات العطرية. قم بتحليل دقيق وتفصيلي للنص التالي واستخرج معلومات النوتات العطرية بعناية.

النص المدخل:
{text}

تعليمات التحليل الدقيقة:
1. اقرأ النص بعناية واستخرج جميع النوتات المذكورة صراحة
2. أسماء النوتات يجب أن تكون فريدة وليست متكررة (تجنب النسخ المكررة)
3. استخرج الاسم الإنجليزي والعربي لكل نوتة (إذا لم يكن العربي موجود، قم بترجمة احترافية)
4. صنف العائلة العطرية بدقة: Floral, Woody, Oriental, Fresh, Fruity, Herbal, Spicy, Amber, Green, Aromatic, Citrus, Oceanic, Gourmand, Chypre, Fougère
5. حدد الدور بناءً على خصائص النوتة: Top (الطيار، الخفيف، التطاير العالي)، Heart/Middle (القلب، الرئيسي)، Base (القاعدة، الثقيل، التطاير المنخفض)
6. حدد التطاير بدقة: High (يتلاشى سريع: 0-30 دقيقة)، Medium (متوسط: 30 دقيقة - 2 ساعة)، Low (ثقيل، يدوم طويل: +2 ساعة)
7. اكتب وصفاً دقيقاً وعمليّاً للنوتة (profile) يعكس خصائصها الحقيقية
8. حدد الاستخدام الأمثل (best_for): مثل "يومي، مناسبات، عمل، مساء، رياضة، الطقس الدافئ، الطقس البارد" إلخ
9. اذكر النوتات التي تتناسب معها بناءً على الكيمياء العطرية
10. اذكر النوتات التي يجب تجنبها (قد تسبب نتائج سيئة)

الصيغة المطلوبة (JSON array نقي):
[
    {{
        "name_en": "اسم إنجليزي (فريد، واضح، صحيح)",
        "name_ar": "الاسم العربي الدقيق",
        "family": "العائلة العطرية",
        "role": "Top أو Heart أو Base",
        "volatility": "High أو Medium أو Low",
        "profile": "وصف دقيق وعمليّ للنوتة (50-100 كلمة)",
        "best_for": ["استخدام1", "استخدام2", "استخدام3"],
        "works_well_with": ["نوتة1", "نوتة2"],
        "avoid_with": ["نوتة1", "نوتة2"],
        "concentration": "نسبة مئوية (10%, 20%, إلخ)",
        "origin": "منشأ، منطقة، أو نوع النبات"
    }}
]

متطلبات أساسية:
- NO duplicate names - كل نوتة يجب أن تكون فريدة
- ALL fields must be filled - جميع الحقول مطلوبة وممتلئة
- Accuracy first - الدقة أهم من الكثرة
- Valid JSON only - JSON صحيح فقط بدون نصوص إضافية"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "أنت خبير في العطور والنوتات العطرية. رد بـ JSON فقط، بدون شرح إضافي."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=4000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # حاول استخراج JSON من الرد (قد يكون مغلف بـ markdown code block)
        try:
            # إذا كان الرد مغلف بـ markdown code block، استخرجه
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end > start:
                    content = content[start:end].strip()
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                if end > start:
                    content = content[start:end].strip()
            
            parsed = json.loads(content)
            if isinstance(parsed, list):
                # تحقق من صحة البيانات
                valid_notes = []
                for note in parsed:
                    if isinstance(note, dict) and note.get('name_en') and note.get('name_ar'):
                        valid_notes.append(note)
                
                if valid_notes:
                    return {
                        'success': True,
                        'notes': valid_notes,
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'error': 'لم يتم استخراج نوتات صحيحة من النص',
                        'notes': []
                    }
            else:
                return {
                    'success': False,
                    'error': 'صيغة الرد غير صحيحة',
                    'notes': []
                }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'خطأ في تحليل الرد: {str(e)[:100]}',
                'notes': []
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'خطأ في الاتصال بـ OpenAI: {str(e)}',
            'notes': []
        }


def find_similar_notes(name_en: str, threshold: float = 0.7) -> list:
    """
    البحث عن نوتات متشابهة في قاعدة البيانات باستخدام fuzzy matching
    
    Args:
        name_en: اسم النوتة الإنجليزية
        threshold: حد التشابه (0-1)، الافتراضي 0.7
    
    Returns:
        قائمة بالنوتات المتشابهة
    """
    from difflib import SequenceMatcher
    from app.models import PerfumeNote
    
    all_notes = PerfumeNote.query.all()
    similar_notes = []
    
    for note in all_notes:
        # حساب نسبة التشابه
        ratio = SequenceMatcher(None, name_en.lower(), note.name_en.lower()).ratio()
        
        if ratio >= threshold:
            similar_notes.append({
                'id': note.id,
                'name_en': note.name_en,
                'name_ar': note.name_ar,
                'similarity_ratio': round(ratio * 100, 1)
            })
    
    # ترتيب حسب نسبة التشابه (الأعلى أولاً)
    similar_notes.sort(key=lambda x: x['similarity_ratio'], reverse=True)
    
    return similar_notes


def generate_daily_scent_suggestion(user):
    """
    تحليل جميع تحليلات المستخدم السابقة وتقديم اقتراح عطري يومي
    التسلسل الهرمي: AnalysisResults → ScentProfile → CustomPerfume
    """
    from app.models import AnalysisResult, DailyScentSuggestion, ScentProfile, CustomPerfume
    from datetime import datetime, date
    from app import db
    import re
    
    try:
        today = date.today()
        existing = DailyScentSuggestion.query.filter_by(
            user_id=user.id, date=today
        ).first()
        
        if existing:
            return {
                'success': True,
                'perfume_name': existing.perfume_name,
                'description': existing.description,
                'reasoning': existing.reasoning,
                'character_type': existing.character_type,
                'from_cache': True
            }
        
        # 1️⃣ محاولة الحصول على AnalysisResults (التحليلات الكاملة)
        analyses = AnalysisResult.query.filter_by(user_id=user.id).order_by(
            AnalysisResult.created_at.desc()
        ).limit(5).all()
        
        context_data = None
        source_type = None
        
        if analyses:
            # استخدام AnalysisResults
            analyses_summary = []
            for a in analyses:
                try:
                    data = json.loads(a.result_data) if a.result_data else {}
                    analyses_summary.append({
                        'module': a.module_name_ar,
                        'data': data
                    })
                except:
                    pass
            context_data = analyses_summary
            source_type = 'analysis_results'
        else:
            # 2️⃣ محاولة الحصول على ScentProfile (تحليلات DNA)
            scent_profiles = ScentProfile.query.filter_by(user_id=user.id).order_by(
                ScentProfile.created_at.desc()
            ).limit(3).all()
            
            if scent_profiles:
                profiles_summary = []
                for p in scent_profiles:
                    profiles_summary.append({
                        'scent_personality': p.scent_personality,
                        'gender': p.gender,
                        'age_range': p.age_range,
                        'personality_type': p.personality_type,
                        'favorite_notes': p.favorite_notes,
                        'climate': p.climate,
                        'skin_type': p.skin_type
                    })
                context_data = profiles_summary
                source_type = 'scent_profile'
            else:
                # 3️⃣ محاولة الحصول على CustomPerfume (العطور المصممة)
                custom_perfumes = CustomPerfume.query.filter_by(user_id=user.id).order_by(
                    CustomPerfume.created_at.desc()
                ).limit(3).all()
                
                if custom_perfumes:
                    perfumes_summary = []
                    for p in custom_perfumes:
                        perfumes_summary.append({
                            'name': p.name,
                            'top_notes': p.top_notes,
                            'heart_notes': p.heart_notes,
                            'base_notes': p.base_notes,
                            'occasion': p.occasion,
                            'intensity': p.intensity
                        })
                    context_data = perfumes_summary
                    source_type = 'custom_perfume'
        
        # 4️⃣ إذا لم يوجد أي بيانات
        if not context_data:
            return {'success': False, 'error': 'لا توجد تحليلات سابقة'}
        
        # بناء الـ prompt بناءً على نوع المصدر
        if source_type == 'analysis_results':
            prompt = f"""أنت خبير عطور متخصص. بناءً على تحليلات المستخدم الشاملة أدناه، قدم اقتراح عطر يومي مخصص بصيغة JSON:

التحليلات: {json.dumps(context_data, ensure_ascii=False)[:1200]}

صيغة JSON (فقط):
{{"perfume_name": "...", "character_type": "...", "description": "...", "reasoning": "..."}}"""
        elif source_type == 'scent_profile':
            prompt = f"""أنت خبير عطور متخصص. بناءً على بصمة عطرية للمستخدم (Scent DNA) أدناه، قدم اقتراح عطر يومي مخصص بصيغة JSON:

بصمته العطرية: {json.dumps(context_data, ensure_ascii=False)[:1200]}

صيغة JSON (فقط):
{{"perfume_name": "...", "character_type": "...", "description": "...", "reasoning": "..."}}"""
        else:  # custom_perfume
            prompt = f"""أنت خبير عطور متخصص. بناءً على العطور المصممة من قبل المستخدم أدناه، قدم اقتراح عطر يومي مخصص بصيغة JSON:

عطوره المصممة: {json.dumps(context_data, ensure_ascii=False)[:1200]}

صيغة JSON (فقط):
{{"perfume_name": "...", "character_type": "...", "description": "...", "reasoning": "..."}}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        
        text = response.choices[0].message.content
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        
        if match:
            data = json.loads(match.group())
            suggestion = DailyScentSuggestion(
                user_id=user.id,
                perfume_name=data.get('perfume_name', 'عطر مقترح'),
                description=data.get('description', ''),
                reasoning=data.get('reasoning', ''),
                character_type=data.get('character_type', ''),
                date=today
            )
            db.session.add(suggestion)
            db.session.commit()
            
            return {
                'success': True,
                'perfume_name': data.get('perfume_name'),
                'description': data.get('description'),
                'reasoning': data.get('reasoning'),
                'character_type': data.get('character_type'),
                'from_cache': False
            }
        
        return {'success': False, 'error': 'فشل في معالجة الرد'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
