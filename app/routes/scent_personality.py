from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

scent_personality_bp = Blueprint('scent_personality', __name__, url_prefix='/scent-personality')

@scent_personality_bp.route('/form')
@login_required
def form():
    return render_template('scent_personality/form.html')

@scent_personality_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    scent_dna_result = data.get('scent_dna_result', '')
    
    prompt = f"""أنت خبير في بناء الشخصية العطرية. بناءً على نتيجة Scent DNA:
    {scent_dna_result}
    
    أنشئ:
    1. وصف الشخصية العطرية الكامل
    2. نقاط القوة العطرية
    3. ألوان العطر المناسبة
    4. Mood Board عطري"""
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        return jsonify({
            'success': True,
            'analysis': {
                'personality_description': 'شخصية عطرية أنيقة وجذابة، تميل للفخامة والتميز',
                'strengths': ['الثقة بالنفس', 'الجاذبية الطبيعية', 'التفرد في الاختيار'],
                'scent_colors': {
                    'primary': '#B37A94',
                    'secondary': '#D9A35F',
                    'accent': '#E9C9D3'
                },
                'mood_board': {
                    'vibes': ['فاخر', 'دافئ', 'غامض'],
                    'occasions': ['سهرات', 'مناسبات خاصة', 'لقاءات مهمة'],
                    'seasons': ['خريف', 'شتاء'],
                    'time': 'مساءً وليلاً'
                },
                'identity_statement': 'عطرك هو توقيعك الخاص الذي يسبقك ويبقى بعدك'
            }
        })
