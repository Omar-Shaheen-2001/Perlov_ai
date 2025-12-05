from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response
from datetime import datetime

adaptive_bp = Blueprint('adaptive', __name__, url_prefix='/adaptive')

@adaptive_bp.route('/form')
@login_required
def form():
    return render_template('adaptive/form.html')

@adaptive_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    current_time = data.get('current_time', datetime.now().strftime('%H:%M'))
    body_temp = data.get('body_temp', 'معتدلة')
    activity = data.get('activity', 'عادي')
    
    hour = int(current_time.split(':')[0]) if ':' in current_time else 12
    
    if hour < 12:
        time_period = 'صباح'
    elif hour < 17:
        time_period = 'ظهر'
    elif hour < 21:
        time_period = 'مساء'
    else:
        time_period = 'ليل'
    
    return jsonify({
        'success': True,
        'analysis': {
            'current_recommendation': {
                'time_period': time_period,
                'perfume': 'Dior Sauvage' if time_period in ['صباح', 'ظهر'] else 'Tom Ford Oud Wood',
                'reason': f'مناسب لفترة {time_period} ونشاطك الحالي'
            },
            'morning_perfume': {
                'name': 'Acqua di Gio',
                'type': 'منعش ونظيف',
                'best_for': 'العمل والنشاطات اليومية'
            },
            'evening_perfume': {
                'name': 'Bleu de Chanel EDP',
                'type': 'أنيق وجذاب',
                'best_for': 'اللقاءات والسهرات'
            },
            'adaptive_tips': [
                'غيّر عطرك حسب الوقت',
                'استخدم عطراً خفيفاً في الحر',
                'العطور القوية للمساء فقط'
            ]
        }
    })
