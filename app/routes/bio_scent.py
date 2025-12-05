from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app import db
from app.models import User
from app.ai_service import save_analysis_result

bio_scent_bp = Blueprint('bio_scent', __name__, url_prefix='/bio-scent', template_folder='../templates/bio_scent')

@bio_scent_bp.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        mood = request.form.get('mood')
        voice_note = request.files.get('voice_note')
        skin_image = request.files.get('skin_image')
        speech_speed = request.form.get('speech_speed')
        
        analysis_result = {
            'mood_analysis': f'تحليل المزاج: {mood}',
            'skin_type': 'معتدلة',
            'fragrance_predictions': ['عطور شرقية دافئة', 'عطور طازجة', 'عطور حساسة'],
            'sensitive_recommendations': 'تم اختيار عطور آمنة للبشرة الحساسة'
        }
        
        return jsonify(analysis_result)
    
    return render_template('bio_scent/form.html')

@bio_scent_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    mood = data.get('mood', '')
    speech_speed = data.get('speech_speed', 'عادية')
    skin_type = data.get('skin_type', 'معتدلة')
    
    result = {
        'voice_analysis': {
            'mood': mood,
            'speech_speed': speech_speed,
            'tone_detected': 'دافئ وهادئ'
        },
        'skin_analysis': {
            'skin_type': skin_type,
            'sensitivity_level': 'متوسطة'
        },
        'fragrance_predictions': [
            'عطور شرقية دافئة',
            'عطور طازجة نقية',
            'عطور حار بنفسجي'
        ],
        'sensitive_recommendations': 'اختيار عطور بنسبة كحول منخفضة وزيوت طبيعية'
    }
    
    save_analysis_result('bio_scent', data, result)
    
    return jsonify(result)
