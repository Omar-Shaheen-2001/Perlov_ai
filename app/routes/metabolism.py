from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

metabolism_bp = Blueprint('metabolism', __name__, url_prefix='/metabolism')

@metabolism_bp.route('/form')
@login_required
def form():
    return render_template('metabolism/form.html')

@metabolism_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    sports_level = data.get('sports_level', '')
    sleep_hours = data.get('sleep_hours', '')
    daily_movement = data.get('daily_movement', '')
    energy_level = data.get('energy_level', '')
    
    prompt = f"""أنت خبير في العلاقة بين الأيض والعطور. حلل:
    - مستوى النشاط الرياضي: {sports_level}
    - ساعات النوم: {sleep_hours}
    - معدل الحركة اليومية: {daily_movement}
    - الطاقة العامة: {energy_level}
    
    قدم توصيات عطرية تتوافق مع معدل الأيض."""
    
    default_analysis = {
        'metabolism_type': 'أيض سريع',
        'strong_perfumes': ['Dior Sauvage Elixir', 'Tom Ford Tobacco Vanille', 'Creed Aventus'],
        'soft_perfumes': ['Jo Malone Wood Sage', 'Byredo Blanche', 'Le Labo Santal 33'],
        'stability_factors': ['استخدم مرطب قبل العطر', 'رش على الملابس أيضاً', 'أعد الرش بعد 4 ساعات'],
        'recommendation': 'بناءً على نشاطك العالي، تحتاج عطور قوية ذات قاعدة ثابتة'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'metabolism_type' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    return jsonify({'success': True, 'analysis': analysis})
