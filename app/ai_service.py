import json
import os
from openai import OpenAI
from flask_login import current_user

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
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
    'recommendations': {'name_ar': 'توصيات العطور', 'icon': 'bi-stars'}
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

def parse_ai_response(content):
    """Safely parse AI response content, handling None and malformed JSON."""
    if content is None:
        return None
    
    result = content.strip()
    
    if result.startswith("```"):
        parts = result.split("```")
        if len(parts) > 1:
            result = parts[1]
            if result.startswith("json"):
                result = result[4:]
    
    result = result.strip()
    
    try:
        return json.loads(result)
    except json.JSONDecodeError:
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

def generate_scent_dna_analysis(profile_data):
    prompt = f"""أنت خبير عطور محترف. قم بتحليل البيانات التالية وأنشئ ملفًا عطريًا شخصيًا (Scent DNA) للمستخدم.

بيانات المستخدم:
- الجنس: {profile_data.get('gender', 'غير محدد')}
- الفئة العمرية: {profile_data.get('age_range', 'غير محدد')}
- نوع الشخصية: {profile_data.get('personality_type', 'غير محدد')}
- النوتات المفضلة: {profile_data.get('favorite_notes', 'غير محدد')}
- النوتات المكروهة: {profile_data.get('disliked_notes', 'غير محدد')}
- المناخ: {profile_data.get('climate', 'غير محدد')}
- نوع البشرة: {profile_data.get('skin_type', 'غير محدد')}

قدم الإجابة بصيغة JSON فقط بالشكل التالي:
{{
    "scent_personality": "اسم الشخصية العطرية (مثل: العاطفي الكلاسيكي، الحيوي العصري، الغامض الشرقي)",
    "personality_description": "وصف مختصر للشخصية العطرية في 2-3 جمل",
    "recommended_families": ["عائلة عطرية 1", "عائلة عطرية 2", "عائلة عطرية 3"],
    "ideal_notes": ["نوتة 1", "نوتة 2", "نوتة 3", "نوتة 4", "نوتة 5"],
    "notes_to_avoid": ["نوتة 1", "نوتة 2"],
    "season_recommendations": "توصيات حسب الموسم",
    "overall_analysis": "تحليل شامل في فقرة واحدة"
}}"""

    default_response = {
        "scent_personality": "الكلاسيكي الأنيق",
        "personality_description": "شخصية عطرية متوازنة تميل للأناقة والرقي",
        "recommended_families": ["شرقية", "خشبية", "زهرية"],
        "ideal_notes": ["عود", "فانيلا", "مسك", "ورد", "عنبر"],
        "notes_to_avoid": profile_data.get('disliked_notes', '').split(',') if profile_data.get('disliked_notes') else [],
        "season_recommendations": "مناسب لجميع الفصول مع تركيز على المساء",
        "overall_analysis": "بناءً على تفضيلاتك، أنت تميل للعطور الكلاسيكية ذات الطابع الشرقي مع لمسات خشبية دافئة."
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير عطور محترف متخصص في تحليل الشخصيات العطرية. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return default_response
        
        return parsed
    except Exception as e:
        default_response["error"] = str(e)
        return default_response

def generate_custom_perfume(perfume_data, scent_profile=None):
    profile_context = ""
    if scent_profile:
        profile_context = f"""
معلومات الملف العطري السابق:
- الشخصية العطرية: {scent_profile.scent_personality or 'غير محدد'}
- النوتات المفضلة: {scent_profile.favorite_notes or 'غير محدد'}
- النوتات المكروهة: {scent_profile.disliked_notes or 'غير محدد'}
"""

    prompt = f"""أنت صانع عطور محترف (Perfumer). قم بتصميم عطر شخصي فريد بناءً على المتطلبات التالية:

متطلبات العطر:
- مناسبة الاستخدام: {perfume_data.get('occasion', 'يومي')}
- درجة الثبات المطلوبة: {perfume_data.get('intensity', 'متوسط')}
- الميزانية: {perfume_data.get('budget', 'متوسطة')}
{profile_context}

صمم عطرًا فريدًا وقدم الإجابة بصيغة JSON فقط:
{{
    "name": "اسم العطر المقترح (اسم إبداعي وجذاب)",
    "name_meaning": "معنى الاسم",
    "top_notes": ["نوتة علوية 1", "نوتة علوية 2", "نوتة علوية 3"],
    "heart_notes": ["نوتة وسطى 1", "نوتة وسطى 2", "نوتة وسطى 3"],
    "base_notes": ["نوتة قاعدية 1", "نوتة قاعدية 2", "نوتة قاعدية 3"],
    "description": "وصف تسويقي جذاب للعطر في 3-4 جمل",
    "match_score": 92,
    "usage_recommendations": "توصيات الاستخدام المثالية",
    "longevity": "مدة الثبات المتوقعة",
    "sillage": "قوة الانتشار (خفيف/متوسط/قوي)",
    "best_seasons": ["الموسم 1", "الموسم 2"]
}}"""

    default_response = {
        "name": "أريج الليل",
        "name_meaning": "عطر الليالي الساحرة",
        "top_notes": ["برغموت", "ليمون", "زنجبيل"],
        "heart_notes": ["ورد", "ياسمين", "زعفران"],
        "base_notes": ["عود", "مسك", "فانيلا"],
        "description": "عطر شرقي فاخر يجمع بين الأناقة والغموض، مثالي للمناسبات الخاصة.",
        "match_score": 90,
        "usage_recommendations": "مثالي للمساء والمناسبات الخاصة",
        "longevity": "8-10 ساعات",
        "sillage": "متوسط إلى قوي",
        "best_seasons": ["الخريف", "الشتاء"]
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت صانع عطور محترف متخصص في ابتكار تركيبات عطرية فريدة. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return default_response
        
        return parsed
    except Exception as e:
        default_response["error"] = str(e)
        return default_response

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

    prompt = f"""أنت خبير عطور محترف ومحلّل روائح متخصص.
مهمتك هي تحديد العطور التي تطابق وصف المستخدم بأعلى دقة ممكنة.

يجب الالتزام بالخطوات التالية دون اختصار:

1) استخرج جميع الإشارات العطرية المذكورة في وصف المستخدم:
- النوتات العليا (Top Notes)
- النوتات الوسطى (Heart Notes)
- النوتات الأساسية (Base Notes)
- نوع العطر (عطري – خشبي – شرقي – فواح – نظيف – حار – ناعم)
- قوة الفوحان (خفيف، متوسط، قوي)
- مدة الثبات المتوقعة
- الأجواء/المزاج المرتبط بالعطر
- الكيميائيات المحددة (Ambroxan، Iso E Super، Incense، إلخ)

2) قارن هذه الإشارات مع قاعدة معرفتك عن العطور المشهورة:
- تطابق النوتات الرئيسية
- تطابق أسلوب العطر
- تطابق الفوحان والثبات
- تطابق الطابع العام

3) أعطِ 3 عطور فقط هي الأقرب للنتيجة (مرتبة من الأكثر تطابقًا إلى الأقل)
لكل عطر يجب أن تذكر:
- اسم العطر الكامل
- درجة التشابه (%)
- سبب التطابق بالتفصيل (قارن الوصف بالنوتات الحقيقية)

4) اعرض قائمة بـ 3-5 عطور لا تتطابق مع الوصف واذكر السبب الواضح.

تعليمات إضافية:
- لا تخمن أبداً
- إذا كان الوصف ناقصاً، قل "الوصف غير كافٍ لتحديد العطر بدقة"
- يُمنع إعطاء عطر لا يتوافق مع الوصف حتى لو كان مشهورًا
- يجب أن تكون المقارنة علمية مبنية على النوتات الحقيقية

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
        "intensity_required": "خفيف/متوسط/قوي",
        "mood_keywords": ["كلمة مفتاحية 1", "كلمة مفتاحية 2"]
    }},
    "top_3_matches": [
        {{
            "rank": 1,
            "name": "اسم العطر الكامل",
            "brand": "العلامة التجارية",
            "match_percentage": 92,
            "actual_notes": {{
                "top": ["نوتة 1", "نوتة 2"],
                "heart": ["نوتة 1", "نوتة 2"],
                "base": ["نوتة 1", "نوتة 2"]
            }},
            "detailed_match_reason": "شرح مفصل لماذا هذا العطر يطابق الوصف. قارن كل نوتة وخصائص العطر مع ما طلبه المستخدم",
            "best_for": "الاستخدام الأمثل",
            "sillage": "قوة الانتشار المتوقعة"
        }}
    ],
    "excluded_fragrances": [
        {{
            "name": "اسم العطر",
            "brand": "العلامة التجارية",
            "exclusion_reason": "السبب الواضح لعدم التطابق (مثال: غياب النوتات الدافئة المطلوبة، أو طابع مختلف تماماً)"
        }}
    ],
    "scientific_conclusion": "ملخص علمي للتطابق والاختلافات",
    "additional_advice": "نصيحة إضافية للمستخدم"
}}"""

    default_response = {
        "scent_analysis": {
            "top_notes_requested": ["برغموت", "ليمون"],
            "heart_notes_requested": ["فلفل", "نعناع"],
            "base_notes_requested": ["عنبر", "مسك"],
            "fragrance_family": "شرقي-عطري",
            "intensity_required": "متوسط",
            "mood_keywords": ["عصري", "جذاب"]
        },
        "top_3_matches": [
            {
                "rank": 1,
                "name": "Dior Sauvage EDP",
                "brand": "Dior",
                "match_percentage": 88,
                "actual_notes": {
                    "top": ["برغموت أمبروكسادي", "ليمون"],
                    "heart": ["فلفل سيشيلي"],
                    "base": ["عنبر جراي", "مسك"]
                },
                "detailed_match_reason": "يطابق الوصف لأنه يحتوي على البرغموت والفلفل المطلوبين، مع قاعدة عنبرية دافئة جداً",
                "best_for": "الاستخدام اليومي والمناسبات",
                "sillage": "متوسط إلى قوي"
            },
            {
                "rank": 2,
                "name": "Bleu de Chanel EDP",
                "brand": "Chanel",
                "match_percentage": 82,
                "actual_notes": {
                    "top": ["برغموت", "ليمون"],
                    "heart": ["ياسمين", "نعناع"],
                    "base": ["خشب الأرز", "مسك"]
                },
                "detailed_match_reason": "يشارك حمضيات البرغموت والليمون، مع نعناع بدل الفلفل، وقاعدة خشبية أكثر برودة",
                "best_for": "العمل والمناسبات الرسمية",
                "sillage": "متوسط"
            },
            {
                "rank": 3,
                "name": "Spicebomb by Viktor & Rolf",
                "brand": "Viktor & Rolf",
                "match_percentage": 75,
                "actual_notes": {
                    "top": ["بهارات", "تفاح"],
                    "heart": ["فلفل أسود", "قرنفل"],
                    "base": ["عنبر", "خشب"]
                },
                "detailed_match_reason": "يوفر الفلفل الأسود والنوتات الدافئة والقاعدة العنبرية، لكن النوتات العليا مختلفة",
                "best_for": "المساء والمناسبات الخاصة",
                "sillage": "قوي"
            }
        ],
        "excluded_fragrances": [
            {
                "name": "Acqua di Gio",
                "brand": "Giorgio Armani",
                "exclusion_reason": "عطر مائي-نظيف بدون قاعدة عنبرية دافئة ولا يحتوي على الفلفل أو التوابل"
            },
            {
                "name": "Light Blue",
                "brand": "Dolce & Gabbana",
                "exclusion_reason": "عطر حمضي خفيف جداً، لا يتطابق مع الطابع الدافئ والعطري المطلوب"
            }
        ],
        "scientific_conclusion": "الوصف يطلب عطراً شرقياً دافئاً مع نوتات حمضية وفلفلية وقاعدة عنبرية قوية",
        "additional_advice": "جرب هذه العطور في متاجر تجار العطور قبل الشراء للتأكد من توافقها مع بشرتك"
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير عطور محترف ومحلّل روائح متخصص. قدم تحليلات دقيقة بناءً على النوتات الحقيقية للعطور. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
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
