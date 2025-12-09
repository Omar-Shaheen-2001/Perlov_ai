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

def generate_article(topic, keywords, tone, language='ar'):
    """Generate a comprehensive article using AI"""
    
    prompt = f"""
    أنت محرر ومؤلف محتوى متخصص في مجال العطور والروائح.
    
    قم بإنشاء مقال شامل حول الموضوع التالي:
    الموضوع: {topic}
    الكلمات المفتاحية: {keywords}
    النبرة: {tone}
    
    يجب أن يتضمن المقال:
    1. عنوان جاذب وخلاق
    2. ملخص قصير (100-150 كلمة)
    3. محتوى غني وشامل (1000-1500 كلمة)
    4. استنتاج قوي
    5. نصائح عملية
    
    أجب بصيغة JSON فقط:
    {{
        "title": "العنوان",
        "summary": "الملخص",
        "content": "المحتوى الكامل",
        "keywords": "كلمات مفتاحية"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت كاتب محتوى متخصص في مجال العطور. أنتج محتوى عالي الجودة وجذاب وغني بالمعلومات. أجب بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2500
        )
        
        content = response.choices[0].message.content
        parsed = parse_ai_response(content)
        
        if parsed is None:
            return {"success": False, "error": "فشل معالجة الرد"}
        
        return {
            "success": True,
            "title": parsed.get('title', f'مقال عن {topic}'),
            "summary": parsed.get('summary', ''),
            "content": parsed.get('content', ''),
            "keywords": parsed.get('keywords', keywords)
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}
