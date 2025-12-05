from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

scent_personality_bp = Blueprint('scent_personality', __name__, url_prefix='/scent-personality')

@scent_personality_bp.route('/form')
@login_required
def form():
    return render_template('scent_personality/form.html')

@scent_personality_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    basic = data.get('basic', {})
    preferences = data.get('preferences', {})
    environmental = data.get('environmental', {})
    emotional = data.get('emotional', {})
    behavioral = data.get('behavioral', {})
    bio_scent = data.get('bio_scent', {})
    
    # Build comprehensive prompt
    prompt = f"""أنت خبير في بناء الشخصية العطرية وعالم النيقة. حلل البيانات التالية وقدم شخصية عطرية شاملة:

البيانات الأساسية:
- العمر: {basic.get('age', '')}
- الجنس: {basic.get('gender', '')}
- أسلوب الحياة: {basic.get('lifestyle', '')}
- نوع الشخصية: {basic.get('personality', '')}

تفضيلات العطور:
- الروائح المفضلة: {', '.join(preferences.get('liked_scents', []))}
- الروائح المكروهة: {preferences.get('disliked_scents', 'لا توجد')}
- درجة القوة: {preferences.get('strength', '')}
- الثبات المفضل: {preferences.get('longevity', '')}

المدخلات البيئية:
- نوع البشرة: {environmental.get('skin_type', '')}
- حرارة الجسم: {environmental.get('body_temperature', '')}
- المناخ: {environmental.get('climate', '')}
- مناسبات الاستخدام: {', '.join(environmental.get('occasions', []))}

المدخلات النفسية:
- ما يريده من العطر: {', '.join(emotional.get('persona', []))}
- اللون المفضل: {emotional.get('color_preference', '')}
- المشاعر المرتبطة: {', '.join(emotional.get('emotions', []))}
- الروائح التي تثير ذكريات: {emotional.get('positive_memories', 'لا توجد')}

المدخلات السلوكية:
- نمط التفاعل: {behavioral.get('scent_behavior', '')}
- معدل الاستخدام: {behavioral.get('usage_frequency', '')}
- الميزانية: {behavioral.get('budget', '')}
- عطور أحبها: {behavioral.get('liked_perfumes', 'لا توجد')}
- عطور لم تعجبه: {behavioral.get('disliked_perfumes', 'لا توجد')}

Bio-Scent:
- نبرة الصوت: {bio_scent.get('voice_tone', 'لم يتم التحديد')}
- جودة الجلد: {bio_scent.get('skin_quality', 'لم يتم التحديد')}
- الحالة المزاجية: {bio_scent.get('current_mood', 'لم يتم التحديد')}

اكشف:
1. وصف الشخصية العطرية الكامل (3-4 جمل)
2. نقاط القوة العطرية (3-4 نقاط)
3. ألوان العطر المناسبة (RGB تقريبي)
4. Mood Board متكامل (الأجواء، المناسبات، المواسم، الوقت)
5. عبارة هوية شخصية فريدة"""
    
    default_analysis = {
        'personality_description': 'شخصية عطرية متوازنة وجذابة، تجمع بين الأناقة والثقة، مع حس فني عالي في اختيار الروائح',
        'strengths': ['التذوق الرفيع', 'الوعي الشخصي العميق', 'القدرة على التعبير الفني', 'الحساسية للتفاصيل'],
        'scent_colors': {
            'primary': '#B37A94',
            'secondary': '#D9A35F',
            'accent': '#E9C9D3'
        },
        'mood_board': {
            'vibes': ['فاخر', 'دافئ', 'غامض', 'مصقول'],
            'occasions': ['سهرات', 'مناسبات خاصة', 'لقاءات مهمة', 'أيام عملية'],
            'seasons': ['خريف', 'شتاء', 'ربيع'],
            'time': 'مساءً وليلاً وأوقات خاصة'
        },
        'identity_statement': 'عطرك هو توقيعك الخاص الذي يسبقك ويبقى بعدك - انعكاس لشخصيتك الفريدة والمصقولة'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'personality_description' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('scent_personality', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
