import json
import os
from openai import OpenAI

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير عطور محترف متخصص في تحليل الشخصيات العطرية. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000
        )
        
        result = response.choices[0].message.content
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        
        return json.loads(result)
    except Exception as e:
        return {
            "scent_personality": "الكلاسيكي الأنيق",
            "personality_description": "شخصية عطرية متوازنة تميل للأناقة والرقي",
            "recommended_families": ["شرقية", "خشبية", "زهرية"],
            "ideal_notes": ["عود", "فانيلا", "مسك", "ورد", "عنبر"],
            "notes_to_avoid": profile_data.get('disliked_notes', '').split(',') if profile_data.get('disliked_notes') else [],
            "season_recommendations": "مناسب لجميع الفصول مع تركيز على المساء",
            "overall_analysis": "بناءً على تفضيلاتك، أنت تميل للعطور الكلاسيكية ذات الطابع الشرقي مع لمسات خشبية دافئة.",
            "error": str(e)
        }

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت صانع عطور محترف متخصص في ابتكار تركيبات عطرية فريدة. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000
        )
        
        result = response.choices[0].message.content
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        
        return json.loads(result)
    except Exception as e:
        return {
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
            "best_seasons": ["الخريف", "الشتاء"],
            "error": str(e)
        }

def generate_recommendations(query, scent_profile=None, products=None):
    profile_context = ""
    if scent_profile:
        profile_context = f"""
الملف العطري للمستخدم:
- الشخصية العطرية: {scent_profile.scent_personality or 'غير محدد'}
- النوتات المفضلة: {scent_profile.favorite_notes or 'غير محدد'}
"""

    products_context = ""
    if products:
        products_list = []
        for p in products[:20]:
            products_list.append(f"- {p.name} من {p.brand}: {p.main_notes}")
        products_context = f"\n\nالعطور المتاحة للتوصية:\n" + "\n".join(products_list)

    prompt = f"""أنت خبير توصيات عطور. المستخدم يبحث عن:
"{query}"
{profile_context}
{products_context}

قدم 5 توصيات عطور مناسبة بصيغة JSON فقط:
{{
    "recommendations": [
        {{
            "name": "اسم العطر",
            "brand": "اسم العلامة التجارية",
            "reason": "سبب التوصية في جملة واحدة",
            "main_notes": "النوتات الرئيسية",
            "match_percentage": 85,
            "best_for": "الاستخدام الأمثل"
        }}
    ],
    "general_advice": "نصيحة عامة للمستخدم"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير توصيات عطور محترف. أجب دائمًا بصيغة JSON فقط."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1500
        )
        
        result = response.choices[0].message.content
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()
        
        return json.loads(result)
    except Exception as e:
        return {
            "recommendations": [
                {
                    "name": "Dior Sauvage",
                    "brand": "Dior",
                    "reason": "عطر رجالي عصري وجذاب",
                    "main_notes": "برغموت، فلفل، عنبر",
                    "match_percentage": 85,
                    "best_for": "الاستخدام اليومي والمناسبات"
                }
            ],
            "general_advice": "جرب العطور قبل الشراء للتأكد من ملاءمتها لبشرتك",
            "error": str(e)
        }
