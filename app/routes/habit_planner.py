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
    
    schedule = data.get('schedule', '')
    daily_activities = data.get('daily_activities', '')
    
    prompt = f"""أنت خبير في تخطيط العطور. أنشئ خطة عطرية بناءً على:
    - جدول المستخدم: {schedule}
    - النشاط اليومي: {daily_activities}
    
    قدم خطة 7 أيام وخطة شهرية."""
    
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
