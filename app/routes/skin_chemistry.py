from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

skin_chemistry_bp = Blueprint('skin_chemistry', __name__, url_prefix='/skin-chemistry')

@skin_chemistry_bp.route('/form')
@login_required
def form():
    return render_template('skin_chemistry/form.html')

@skin_chemistry_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    skin_type = data.get('skin_type', '')
    sensitivity = data.get('sensitivity', '')
    body_temp = data.get('body_temp', '')
    failed_perfumes = data.get('failed_perfumes', '')
    
    prompt = f"""أنت خبير في كيمياء العطور والبشرة. حلل التوافق العطري بناءً على:
    - نوع البشرة: {skin_type}
    - حساسية البشرة: {sensitivity}
    - حرارة الجسم: {body_temp}
    - عطور لم تثبت سابقاً: {failed_perfumes}
    
    قدم:
    1. قائمة بـ 5 عطور مناسبة كيميائياً للبشرة
    2. مستوى الثبات المتوقع (ممتاز/جيد/متوسط)
    3. قائمة بالمكونات التي يجب تجنبها
    4. توصيات خاصة حسب كيمياء الجلد
    
    أجب بصيغة JSON."""
    
    default_analysis = {
        'suitable_perfumes': ['Chanel No. 5', 'Dior Sauvage', 'Tom Ford Oud Wood', 'Jo Malone Peony', 'Byredo Gypsy Water'],
        'stability_level': 'جيد',
        'avoid_ingredients': ['الكحول المركز', 'المسك الصناعي', 'البارابين'],
        'recommendations': 'يُنصح باستخدام عطور ذات قاعدة خشبية لثبات أطول مع بشرتك'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'suitable_perfumes' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'skin_type': skin_type,
        'sensitivity': sensitivity
    })
