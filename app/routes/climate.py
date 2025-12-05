from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

climate_bp = Blueprint('climate', __name__, url_prefix='/climate')

@climate_bp.route('/form')
@login_required
def form():
    return render_template('climate/form.html')

@climate_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    country = data.get('country', '')
    temperature = data.get('temperature', '')
    humidity = data.get('humidity', '')
    season = data.get('season', '')
    
    prompt = f"""أنت خبير في العطور والمناخ. حلل:
    - البلد/المدينة: {country}
    - الحرارة: {temperature}
    - الرطوبة: {humidity}
    - الموسم: {season}
    
    قدم توصيات عطرية مناسبة للمناخ."""
    
    default_analysis = {
        'summer_perfumes': ['Acqua di Gio', 'Light Blue', 'CK One Summer'],
        'winter_perfumes': ['Spicebomb', 'The One EDP', 'Tobacco Vanille'],
        'sillage_level': 'متوسط - مناسب للحرارة العالية',
        'hot_weather_options': ['عطور مائية', 'حمضيات منعشة', 'نوتات خضراء'],
        'recommendation': 'للمناخ الحار، اختر عطور خفيفة بتركيز EDT'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'summer_perfumes' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('climate', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
