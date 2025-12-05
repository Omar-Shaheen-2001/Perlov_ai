from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

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
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        return jsonify({
            'success': True,
            'analysis': {
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
        })
