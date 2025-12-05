from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

oil_mixer_bp = Blueprint('oil_mixer', __name__, url_prefix='/oil-mixer')

@oil_mixer_bp.route('/form')
@login_required
def form():
    return render_template('oil_mixer/form.html')

@oil_mixer_bp.route('/mix', methods=['POST'])
@login_required
def mix():
    data = request.get_json()
    
    selected_notes = data.get('notes', [])
    target_layer = data.get('target', 'قلب')
    
    prompt = f"""أنت خبير في مزج النوتات العطرية. امزج:
    - النوتات المختارة: {', '.join(selected_notes)}
    - الهدف: {target_layer}
    
    أنشئ أكورداً عطرياً متناسقاً."""
    
    default_analysis = {
        'accord_name': 'Oriental Harmony',
        'notes_used': selected_notes if selected_notes else ['الورد', 'العنبر', 'المسك'],
        'mixing_ratios': {
            'note_1': '40%',
            'note_2': '35%',
            'note_3': '25%'
        },
        'description': 'أكورد شرقي دافئ يجمع بين الأناقة والغموض',
        'layer_type': target_layer,
        'compatibility': 'يتناسب مع قواعد خشبية وعنبرية',
        'tips': [
            'أضف نوتة حمضية للمقدمة',
            'استخدم قاعدة من خشب الصندل',
            'يمكن تخفيفه بنوتات زهرية'
        ]
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'accord_name' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    return jsonify({'success': True, 'analysis': analysis})
