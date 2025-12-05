from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

occasion_bp = Blueprint('occasion', __name__, url_prefix='/occasion')

@occasion_bp.route('/form')
@login_required
def form():
    return render_template('occasion/form.html')

@occasion_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    occasion_type = data.get('occasion_type', '')
    
    prompt = f"""أنت خبير في اختيار العطور للمناسبات. قدم توصيات لمناسبة:
    {occasion_type}
    
    قدم أفضل 3 عطور مع نصائح وخيارات سعرية."""
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        occasions_data = {
            'زواج': {
                'perfumes': [
                    {'name': 'Chanel Coco Mademoiselle', 'price': 'فاخر', 'why': 'أنيق ورومانسي'},
                    {'name': 'Lancôme La Vie Est Belle', 'price': 'متوسط', 'why': 'سعيد ومشرق'},
                    {'name': 'Viktor & Rolf Flowerbomb', 'price': 'فاخر', 'why': 'زهري قوي'}
                ],
                'tips': ['رشي بخفة لتجنب الإزعاج', 'اختاري عطراً يدوم طوال الحفل']
            },
            'عمل': {
                'perfumes': [
                    {'name': 'Chanel Bleu', 'price': 'فاخر', 'why': 'احترافي وأنيق'},
                    {'name': 'Dior Homme', 'price': 'متوسط', 'why': 'كلاسيكي'},
                    {'name': 'Versace Pour Homme', 'price': 'اقتصادي', 'why': 'منعش ومناسب'}
                ],
                'tips': ['تجنب العطور القوية', 'اختر عطراً نظيفاً']
            }
        }
        return jsonify({
            'success': True,
            'analysis': occasions_data.get(occasion_type, occasions_data['عمل'])
        })
