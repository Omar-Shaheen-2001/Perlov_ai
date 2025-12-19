from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

habit_planner_bp = Blueprint('habit_planner', __name__, url_prefix='/habit-planner')

@habit_planner_bp.route('/form')
@login_required
def form():
    return render_template('habit_planner/form.html')

@habit_planner_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    gender = data.get('gender', '')
    age_range = data.get('age_range', '')
    climate = data.get('climate', '')
    skin_type = data.get('skin_type', '')
    scent_intensity = data.get('scent_intensity', '2')
    longevity = data.get('longevity', '')
    fragrance_family = data.get('fragrance_family', [])
    schedule = data.get('schedule', '')
    daily_activities = data.get('daily_activities', '')
    current_perfumes = data.get('current_perfumes', '')
    
    # تحويل قيم الفوحان والثبات
    intensity_map = {'1': 'خفيف', '2': 'متوسط', '3': 'قوي'}
    intensity_text = intensity_map.get(scent_intensity, 'متوسط')
    
    fragrance_text = ', '.join(fragrance_family) if fragrance_family else 'متنوعة'
    current_perf_text = current_perfumes if current_perfumes else 'لا توجد عطور حالية'
    
    prompt = f"""أنت خبير في تخطيط العطور المتقدم. أنشئ خطة عطرية شاملة بناءً على المعلومات التالية:

المعلومات الشخصية:
- الجنس: {gender}
- الفئة العمرية: {age_range}
- المناخ: {climate}
- نوع البشرة: {skin_type}
- قوة الفوحان المفضلة: {intensity_text}
- ثبات العطر المفضل: {longevity}

التفضيلات العطرية:
- العائلات المفضلة: {fragrance_text}
- العطور الحالية: {current_perf_text}

جدول الحياة:
- الجدول الأسبوعي: {schedule}
- النشاط اليومي: {daily_activities}

قدم:
1. خطة 7 أيام محددة مع عطر مناسب لكل يوم
2. نصائح شهرية مخصصة لهذا الملف العطري
3. توصيات بناءً على نوع البشرة والمناخ"""
    
    default_analysis = {
        'weekly_plan': {
            'السبت': {'perfume': 'Dior Sauvage', 'reason': 'بداية الأسبوع بنشاط'},
            'الأحد': {'perfume': 'Bleu de Chanel', 'reason': 'احترافي للعمل'},
            'الإثنين': {'perfume': 'Versace Dylan Blue', 'reason': 'منعش ونظيف'},
            'الثلاثاء': {'perfume': 'Prada L\'Homme', 'reason': 'أنيق وهادئ'},
            'الأربعاء': {'perfume': 'YSL Y EDP', 'reason': 'منتصف الأسبوع بقوة'},
            'الخميس': {'perfume': 'Chanel Allure', 'reason': 'تحضير لعطلة الأسبوع'},
            'الجمعة': {'perfume': 'Tom Ford Oud Wood', 'reason': 'فاخر ليوم الإجازة'}
        },
        'monthly_tips': [
            'بدّل بين 3-4 عطور لتجنب التعود',
            'خصص عطراً للمناسبات الخاصة',
            'احتفظ بعطر خفيف للصيف وقوي للشتاء'
        ]
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'weekly_plan' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('habit_planner', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
