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
    
    أنشئ ملفاً عصبياً عطرياً شاملاً مع اقتراحات عطور مناسبة."""
    
    default_analysis = {
        'neural_profile': 'شخصية عاطفية حساسة',
        'mood_recommendations': ['عطور دافئة للراحة', 'حمضيات للنشاط', 'فانيليا للسعادة'],
        'emotional_notes': {
            'happiness': ['البرتقال', 'الياسمين', 'الفانيليا'],
            'calm': ['اللافندر', 'خشب الصندل', 'البخور'],
            'energy': ['النعناع', 'الليمون', 'الزنجبيل']
        },
        'color_scent_match': 'الألوان الدافئة تتوافق مع العطور الشرقية',
        'memory_triggers': 'ذكرياتك مرتبطة بنوتات الأزهار والخشب',
        'recommended_perfumes': [
            {
                'name': 'Maison Francis Kurkdjian Baccarat Rouge 540',
                'category': 'للسعادة والفرح',
                'notes': 'زعفران، عنبر، أرز',
                'why': 'يحفز مراكز السعادة في الدماغ بنوتاته الدافئة'
            },
            {
                'name': 'Chanel Chance Eau Tendre',
                'category': 'للهدوء والاسترخاء',
                'notes': 'جريب فروت، ياسمين، مسك أبيض',
                'why': 'يخفض التوتر ويحسن المزاج بنوتاته الناعمة'
            },
            {
                'name': 'Tom Ford Oud Wood',
                'category': 'للذكريات العميقة',
                'notes': 'عود، خشب الورد، فانيليا',
                'why': 'يربط بين الذكريات والمشاعر الإيجابية'
            },
            {
                'name': 'Jo Malone English Pear & Freesia',
                'category': 'للنشاط والطاقة',
                'notes': 'كمثرى، فريزيا، مسك',
                'why': 'ينشط الدماغ ويزيد التركيز والإنتاجية'
            },
            {
                'name': 'Dior Sauvage Elixir',
                'category': 'للثقة بالنفس',
                'notes': 'لافندر، خشب الصندل، عنبر',
                'why': 'يعزز الشعور بالقوة والسيطرة'
            }
        ]
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'neural_profile' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    return jsonify({'success': True, 'analysis': analysis})
