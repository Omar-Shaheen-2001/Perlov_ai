from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import analyze_face_for_perfume, save_analysis_result

face_analyzer_bp = Blueprint('face_analyzer', __name__, url_prefix='/face-analyzer')

@face_analyzer_bp.route('/form')
@login_required
def form():
    return render_template('face_analyzer/form.html')

@face_analyzer_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    image_data = data.get('image_data', '')
    
    if not image_data:
        return jsonify({
            'success': False,
            'error': 'لم يتم توفير صورة للتحليل'
        }), 400
    
    try:
        analysis = analyze_face_for_perfume(image_data)
        
        if 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 500
        
        save_analysis_result('face_analyzer', {'image_provided': True}, analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
