from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result

signature_bp = Blueprint('signature', __name__, url_prefix='/signature')

@signature_bp.route('/form')
@login_required
def form():
    return render_template('signature/form.html')

@signature_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    representing_scents = data.get('representing_scents', '')
    lifestyle = data.get('lifestyle', '')
    main_occasion = data.get('main_occasion', '')
    
    prompt = f"""أنت خبير في بناء العطور التوقيعية. صمم عطراً توقيعياً بناءً على:
    - الروائح التي تمثل المستخدم: {representing_scents}
    - أسلوب الحياة: {lifestyle}
    - المناسبة الأساسية: {main_occasion}
    
    أنشئ وصفاً كاملاً للعطر التوقيعي."""
    
    default_analysis = {
        'signature_name': 'Essence of You',
        'description': 'عطر توقيعي فريد يجمع بين الأناقة والدفء، مصمم ليعكس شخصيتك الحقيقية',
        'notes': {
            'top': ['البرغموت', 'الفلفل الوردي'],
            'heart': ['الورد', 'العنبر'],
            'base': ['خشب الصندل', 'المسك الأبيض']
        },
        'wearing_guide': {
            'occasion': 'كل يوم - عطرك الدائم',
            'application': 'رش على نقاط النبض صباحاً',
            'layering': 'يمكن دمجه مع عطر مسائي أقوى'
        },
        'uniqueness': 'هذا العطر صُمم خصيصاً ليكون هويتك العطرية التي لا تُنسى'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'signature_name' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    save_analysis_result('signature', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
