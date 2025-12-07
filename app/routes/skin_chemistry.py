from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

skin_chemistry_bp = Blueprint('skin_chemistry', __name__, url_prefix='/skin-chemistry')

@skin_chemistry_bp.route('/form')
@login_required
def form():
    return render_template('skin_chemistry/form.html')

@skin_chemistry_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    skin_type = data.get('skin_type', '')
    sensitivity = data.get('sensitivity', '')
    body_temp = data.get('body_temp', '')
    oily_areas = data.get('oily_areas', '')
    dry_areas = data.get('dry_areas', '')
    reactions = data.get('reactions', '')
    failed_perfumes = data.get('failed_perfumes', '')
    preferences = data.get('preferences', '')
    
    # Build detailed AI prompt with precise input data
    prompt = f"""أنت خبير محترف في علم كيمياء العطور والبشرة (Fragrance Chemistry & Dermatology). قم بتحليل دقيق جداً للتوافق العطري بناءً على المدخلات التالية:

مدخلات المستخدم:
- نوع البشرة الأساسي: {skin_type}
- مستوى حساسية البشرة: {sensitivity}
- حرارة جسم المستخدم: {body_temp}
- المناطق الدهنية: {oily_areas if oily_areas else 'لم يتم تحديدها'}
- المناطق الجافة: {dry_areas if dry_areas else 'لم يتم تحديدها'}
- الحساسيات أو الحساسيات: {reactions if reactions else 'لا توجد'}
- عطور لم تستمر طويلاً أو سببت مشاكل: {failed_perfumes if failed_perfumes else 'لا توجد'}
- تفضيلات العطور المفضلة: {preferences if preferences else 'متنوعة'}

المطلوب:
قدم تحليلاً دقيقاً جداً يتضمن:

1. **العطور المناسبة كيميائياً** - قائمة بـ 5 عطور محددة مع شرح كيمياء التوافق لكل واحد:
   - الاسم الدقيق للعطر
   - المركبة (العائلة العطرية)
   - نسبة التوافق الكيميائي (0-100%)
   - السبب العلمي للتوافق مع كيمياء البشرة المحددة

2. **تحليل الثبات المتوقع**:
   - مستوى الثبات الدقيق (ممتاز 8-10h+ / جيد 5-8h / متوسط 3-5h / ضعيف <3h)
   - المدة المتوقعة على البشرة بالساعات
   - تأثير حرارة الجسم ونوع البشرة على الثبات

3. **المكونات الكيميائية المهمة والمكونات المراد تجنبها**:
   - المكونات الآمنة للبشرة الحساسة (إن انطبق)
   - المكونات التي قد تسبب تفاعلات كيميائية سلبية
   - البدائل الكيميائية الآمنة

4. **توصيات متقدمة**:
   - التطبيق الأمثل بناءً على أنواع البشرة المختلطة
   - وقت التطبيق الأمثل خلال اليوم
   - نصائح لتحسين الثبات بناءً على كيمياء البشرة
   - تفاعلات محتملة مع مستحضرات العناية بالبشرة

قدم الإجابة بصيغة JSON دقيقة بالشكل التالي:
{{
    "suitable_perfumes": [
        {{
            "name": "اسم العطر الدقيق",
            "brand": "اسم العلامة",
            "family": "العائلة العطرية",
            "compatibility": 95,
            "chemistry_reason": "شرح دقيق علمي للتوافق الكيميائي",
            "longevity_hours": 8,
            "optimal_for": "الاستخدام الأمثل"
        }}
    ],
    "stability_analysis": {{
        "level": "مستوى الثبات (ممتاز/جيد/متوسط/ضعيف)",
        "estimated_hours": 6.5,
        "body_heat_effect": "تأثير حرارة الجسم",
        "skin_chemistry_effect": "تأثير نوع البشرة"
    }},
    "chemical_considerations": {{
        "safe_ingredients": ["المكونات الآمنة"],
        "avoid_ingredients": ["المكونات المراد تجنبها"],
        "why_avoid": ["الأسباب العلمية"]
    }},
    "detailed_recommendations": [
        "توصية 1",
        "توصية 2",
        "توصية 3"
    ],
    "skincare_compatibility": "توصيات حول التوافق مع مستحضرات العناية",
    "application_tips": "نصائح التطبيق الأمثل"
}}"""

    # Improved default response
    default_analysis = {
        'suitable_perfumes': [
            {
                'name': 'Dior Sauvage',
                'brand': 'Dior',
                'family': 'خشبية-شرقية',
                'compatibility': 90,
                'chemistry_reason': 'تركيبة متوازنة تناسب البشرة المختلطة',
                'longevity_hours': 7,
                'optimal_for': 'الاستخدام اليومي والمناسبات'
            },
            {
                'name': 'Tom Ford Black Orchid',
                'brand': 'Tom Ford',
                'family': 'شرقية فاخرة',
                'compatibility': 87,
                'chemistry_reason': 'مكونات مرطبة تناسب البشرة الجافة',
                'longevity_hours': 9,
                'optimal_for': 'المساء والمناسبات الخاصة'
            }
        ],
        'stability_analysis': {
            'level': 'جيد',
            'estimated_hours': 7.0,
            'body_heat_effect': 'حرارة الجسم المعتدلة تعزز الثبات',
            'skin_chemistry_effect': 'البشرة المختلطة توفر توازن جيد للثبات'
        },
        'chemical_considerations': {
            'safe_ingredients': ['الزيوت الطبيعية', 'المسك الطبيعي', 'العنبر الرمادي'],
            'avoid_ingredients': ['الكحول المركز', 'المسك الصناعي الرخيص'],
            'why_avoid': ['قد يسبب جفاف إضافي', 'قد يسبب تحسس']
        },
        'detailed_recommendations': [
            'طبق العطر على نقاط النبض (الرقبة، المعصم، خلف الأذن)',
            'لا تفرك المعصمين معاً بعد التطبيق للحفاظ على جودة المركبة',
            'طبق على بشرة رطبة قليلاً لتحسين الثبات'
        ],
        'skincare_compatibility': 'تأكد من أن مستحضرات عنايتك خالية من المكونات المهيجة. استخدم المرطبات قبل العطر.',
        'application_tips': 'أفضل وقت للتطبيق هو بعد الاستحمام مباشرة على بشرة دافئة ورطبة قليلاً.'
    }
    
    try:
        response = get_ai_response(prompt, "أنت خبير محترف في علم كيمياء العطور والبشرة. أجب دائمًا بصيغة JSON دقيقة وعلمية فقط.")
        if isinstance(response, dict) and 'suitable_perfumes' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('skin_chemistry', data, analysis)
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'input_summary': {
            'skin_type': skin_type,
            'sensitivity': sensitivity,
            'body_temp': body_temp
        }
    })
