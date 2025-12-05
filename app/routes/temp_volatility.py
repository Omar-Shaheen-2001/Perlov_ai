from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

temp_volatility_bp = Blueprint('temp_volatility', __name__, url_prefix='/temp-volatility')

@temp_volatility_bp.route('/form')
@login_required
def form():
    return render_template('temp_volatility/form.html')

@temp_volatility_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    activity_level = data.get('activity_level', '')
    body_temp = data.get('body_temp', '')
    climate = data.get('climate', '')
    preferred_time = data.get('preferred_time', '')
    
    prompt = f"""أنت خبير في تطاير العطور وحرارة الجسم. حلل:
    - مستوى النشاط اليومي: {activity_level}
    - حرارة الجسم: {body_temp}
    - المناخ: {climate}
    - الوقت المفضل: {preferred_time}
    
    قدم:
    1. معدل تطاير العطر المناسب
    2. الثبات في الأجواء الحارة والباردة
    3. أفضل وقت للاستخدام
    4. اقتراح تركيز (EDT / EDP / Extrait)
    
    أجب بصيغة JSON."""
    
    default_analysis = {
        'volatility_rate': 'متوسط - يتطاير خلال 4-6 ساعات',
        'hot_weather_stability': 'جيد مع تركيز EDP',
        'cold_weather_stability': 'ممتاز مع أي تركيز',
        'best_time': 'المساء والليل',
        'recommended_concentration': 'EDP - Eau de Parfum',
        'tips': 'رش على نقاط النبض للحصول على ثبات أطول'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'volatility_rate' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('temp_volatility', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
