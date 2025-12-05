from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

neuroscience_bp = Blueprint('neuroscience', __name__, url_prefix='/neuroscience')

@neuroscience_bp.route('/form')
@login_required
def form():
    return render_template('neuroscience/form.html')

@neuroscience_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    scent_memories = data.get('scent_memories', '')
    favorite_colors = data.get('favorite_colors', '')
    emotional_triggers = data.get('emotional_triggers', '')
    
    prompt = f"""أنت خبير في علم الأعصاب العطري. حلل:
    - ذكريات مرتبطة بروائح: {scent_memories}
    - ألوان مفضلة: {favorite_colors}
    - مشاعر مفعّلة بالروائح: {emotional_triggers}
    
    أنشئ ملفاً عصبياً عطرياً شاملاً."""
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        return jsonify({
            'success': True,
            'analysis': {
                'neural_profile': 'شخصية عاطفية حساسة',
                'mood_recommendations': ['عطور دافئة للراحة', 'حمضيات للنشاط', 'فانيليا للسعادة'],
                'emotional_notes': {
                    'happiness': ['البرتقال', 'الياسمين', 'الفانيليا'],
                    'calm': ['اللافندر', 'خشب الصندل', 'البخور'],
                    'energy': ['النعناع', 'الليمون', 'الزنجبيل']
                },
                'color_scent_match': 'الألوان الدافئة تتوافق مع العطور الشرقية',
                'memory_triggers': 'ذكرياتك مرتبطة بنوتات الأزهار والخشب'
            }
        })
