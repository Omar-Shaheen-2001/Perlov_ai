from flask import Blueprint, render_template, jsonify, session
from flask_login import login_required, current_user
from app.models import ScentProfile, CustomPerfume, Recommendation, AnalysisResult, DailyScentSuggestion
from app.ai_service import generate_daily_scent_suggestion
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    scent_profiles = ScentProfile.query.filter_by(user_id=current_user.id).order_by(ScentProfile.created_at.desc()).all()
    custom_perfumes = CustomPerfume.query.filter_by(user_id=current_user.id).order_by(CustomPerfume.created_at.desc()).all()
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.created_at.desc()).all()
    analysis_results = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(AnalysisResult.created_at.desc()).all()
    
    latest_profile = scent_profiles[0] if scent_profiles else None
    latest_perfume = custom_perfumes[0] if custom_perfumes else None
    
    # الحصول على الاقتراح العطري اليومي
    daily_suggestion = None
    if analysis_results:
        result = generate_daily_scent_suggestion(current_user)
        if result.get('success'):
            daily_suggestion = result
    
    stats = {
        'profiles_count': len(scent_profiles),
        'perfumes_count': len(custom_perfumes),
        'recommendations_count': len(recommendations),
        'analysis_count': len(analysis_results)
    }
    
    return render_template('dashboard/index.html', 
                         latest_profile=latest_profile,
                         latest_perfume=latest_perfume,
                         scent_profiles=scent_profiles,
                         custom_perfumes=custom_perfumes,
                         recommendations=recommendations,
                         analysis_results=analysis_results,
                         daily_suggestion=daily_suggestion,
                         stats=stats)

@dashboard_bp.route('/dashboard/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    analysis = AnalysisResult.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    
    result_data = None
    input_data = None
    
    try:
        if analysis.result_data:
            result_data = json.loads(analysis.result_data)
    except:
        result_data = analysis.result_data
    
    try:
        if analysis.input_data:
            input_data = json.loads(analysis.input_data)
    except:
        input_data = analysis.input_data
    
    return render_template('dashboard/analysis_detail.html', 
                          analysis=analysis,
                          result_data=result_data,
                          input_data=input_data)

@dashboard_bp.route('/dashboard/all-analyses')
@login_required
def all_analyses():
    analysis_results = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(AnalysisResult.created_at.desc()).all()
    
    return render_template('dashboard/all_analyses.html', 
                         analysis_results=analysis_results)

@dashboard_bp.route('/dashboard/api/analysis/<int:analysis_id>')
@login_required
def api_analysis(analysis_id):
    analysis = AnalysisResult.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    
    result_data = None
    input_data = None
    
    try:
        if analysis.result_data:
            result_data = json.loads(analysis.result_data)
    except:
        result_data = analysis.result_data
    
    try:
        if analysis.input_data:
            input_data = json.loads(analysis.input_data)
    except:
        input_data = analysis.input_data
    
    return jsonify({
        'id': analysis.id,
        'module_type': analysis.module_type,
        'module_name_ar': analysis.module_name_ar,
        'module_icon': analysis.module_icon,
        'input_data': input_data,
        'result_data': result_data,
        'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M')
    })

@dashboard_bp.route('/dashboard/api/daily-suggestion')
@login_required
def api_daily_suggestion():
    result = generate_daily_scent_suggestion(current_user)
    return jsonify(result)
