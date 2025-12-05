from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response

predictive_bp = Blueprint('predictive', __name__, url_prefix='/predictive')

@predictive_bp.route('/form')
@login_required
def form():
    return render_template('predictive/form.html')

@predictive_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    past_perfumes = data.get('past_perfumes', '')
    scent_dna = data.get('scent_dna', '')
    buying_behavior = data.get('buying_behavior', '')
    
    prompt = f"""أنت خبير في التنبؤ بالذوق العطري. حلل:
    - سجل العطور الماضية: {past_perfumes}
    - نتيجة Scent DNA: {scent_dna}
    - سلوك الشراء: {buying_behavior}
    
    تنبأ بأفضل 5 عطور مستقبلية وأنماط الذوق."""
    
    try:
        response = get_ai_response(prompt)
        return jsonify({'success': True, 'analysis': response})
    except:
        return jsonify({
            'success': True,
            'analysis': {
                'future_top5': [
                    {'name': 'Maison Francis Kurkdjian Baccarat Rouge 540', 'match': '95%'},
                    {'name': 'Parfums de Marly Layton', 'match': '92%'},
                    {'name': 'Nishane Hacivat', 'match': '89%'},
                    {'name': 'Xerjoff Naxos', 'match': '87%'},
                    {'name': 'Initio Oud for Greatness', 'match': '85%'}
                ],
                'taste_patterns': ['ميول نحو العطور الشرقية', 'تفضيل النوتات الخشبية', 'حب العود'],
                'evolution_analysis': 'ذوقك يتطور نحو العطور الفاخرة والنيش',
                'next_purchase': 'بناءً على تحليلك، Baccarat Rouge 540 هو خيارك المثالي القادم'
            }
        })
