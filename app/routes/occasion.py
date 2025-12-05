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
        },
        'سفر': {
            'perfumes': [
                {'name': 'Acqua di Gio', 'price': 'متوسط', 'why': 'منعش للسفر الطويل'},
                {'name': 'Light Blue', 'price': 'متوسط', 'why': 'خفيف ومريح'},
                {'name': 'CK One', 'price': 'اقتصادي', 'why': 'نظيف ومحايد'}
            ],
            'tips': ['اختر عطراً خفيفاً', 'احمل نسخة صغيرة للتجديد']
        },
        'سهرة': {
            'perfumes': [
                {'name': 'Tom Ford Oud Wood', 'price': 'فاخر', 'why': 'فاخر وغامض'},
                {'name': 'Dior Sauvage Elixir', 'price': 'فاخر', 'why': 'قوي وجذاب'},
                {'name': 'YSL La Nuit de L\'Homme', 'price': 'متوسط', 'why': 'رومانسي'}
            ],
            'tips': ['استخدم عطراً قوياً', 'رش على نقاط النبض']
        },
        'رياضة': {
            'perfumes': [
                {'name': 'Versace Pour Homme', 'price': 'اقتصادي', 'why': 'منعش ونشط'},
                {'name': 'Nautica Voyage', 'price': 'اقتصادي', 'why': 'بحري منعش'},
                {'name': 'Cool Water', 'price': 'اقتصادي', 'why': 'كلاسيكي رياضي'}
            ],
            'tips': ['استخدم عطراً خفيفاً', 'تجنب العطور الثقيلة']
        },
        'يومي': {
            'perfumes': [
                {'name': 'Bleu de Chanel', 'price': 'فاخر', 'why': 'مناسب لكل مناسبة'},
                {'name': 'Dior Sauvage', 'price': 'متوسط', 'why': 'عصري ومتنوع'},
                {'name': 'Prada L\'Homme', 'price': 'متوسط', 'why': 'أنيق وهادئ'}
            ],
            'tips': ['اختر عطراً متوازناً', 'يمكن استخدامه صباحاً ومساءً']
        }
    }
    
    default_analysis = occasions_data.get(occasion_type, occasions_data['يومي'])
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'perfumes' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    return jsonify({'success': True, 'analysis': analysis})
