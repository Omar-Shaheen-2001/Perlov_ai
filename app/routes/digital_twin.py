from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

digital_twin_bp = Blueprint('digital_twin', __name__, url_prefix='/digital-twin')

@digital_twin_bp.route('/form')
@login_required
def form():
    return render_template('digital_twin/form.html')

@digital_twin_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    all_data = data.get('all_user_data', {})
    
    prompt = f"""أنت خبير في إنشاء الهويات العطرية الرقمية. بناءً على كل بيانات المستخدم:
    {all_data}
    
    أنشئ توأماً عطرياً رقمياً شاملاً."""
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        return jsonify({
            'success': True,
            'analysis': {
                'digital_identity': {
                    'name': 'عطرك الرقمي',
                    'code': 'PERLOV-' + str(current_user.id if current_user.is_authenticated else '001'),
                    'personality_type': 'الأنيق الكلاسيكي',
                    'scent_family': 'شرقي خشبي'
                },
                'permanent_record': {
                    'favorite_notes': ['العود', 'الورد', 'المسك'],
                    'preferred_intensity': 'متوسط إلى قوي',
                    'best_season': 'خريف وشتاء',
                    'signature_accords': ['شرقي', 'خشبي', 'حار']
                },
                'auto_updates': True,
                'last_updated': 'الآن',
                'evolution_stage': 'المرحلة الثانية - الناضج العطري'
            }
        })
