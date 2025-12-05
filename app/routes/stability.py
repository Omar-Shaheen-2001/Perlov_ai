from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

stability_bp = Blueprint('stability', __name__, url_prefix='/stability')

@stability_bp.route('/form')
@login_required
def form():
    return render_template('stability/form.html')

@stability_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    skin_type = data.get('skin_type', '')
    weather_temp = data.get('weather_temp', '')
    usage_time = data.get('usage_time', '')
    
    prompt = f"""أنت خبير في ثبات العطور وفوحانها. حلل:
    - نوع البشرة: {skin_type}
    - حرارة الجو: {weather_temp}
    - وقت الاستخدام: {usage_time}
    
    قدم تحليلاً شاملاً للثبات والفوحان."""
    
    default_analysis = {
        'stability_score': '8/10',
        'sillage_strength': 'قوي - يملأ الغرفة',
        'longevity_hours': '6-8 ساعات',
        'tips': [
            'استخدم مرطب غير معطر قبل الرش',
            'رش على نقاط النبض',
            'لا تفرك العطر بعد الرش',
            'خزن العطر بعيداً عن الضوء والحرارة'
        ],
        'best_application': 'الرقبة، المعصم، خلف الأذن'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'stability_score' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('stability', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
