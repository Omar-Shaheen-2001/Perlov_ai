from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import ScentProfile, CustomPerfume, Recommendation

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    scent_profiles = ScentProfile.query.filter_by(user_id=current_user.id).order_by(ScentProfile.created_at.desc()).all()
    custom_perfumes = CustomPerfume.query.filter_by(user_id=current_user.id).order_by(CustomPerfume.created_at.desc()).all()
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.created_at.desc()).all()
    
    latest_profile = scent_profiles[0] if scent_profiles else None
    latest_perfume = custom_perfumes[0] if custom_perfumes else None
    
    stats = {
        'profiles_count': len(scent_profiles),
        'perfumes_count': len(custom_perfumes),
        'recommendations_count': len(recommendations)
    }
    
    return render_template('dashboard/index.html', 
                         latest_profile=latest_profile,
                         latest_perfume=latest_perfume,
                         scent_profiles=scent_profiles,
                         custom_perfumes=custom_perfumes,
                         recommendations=recommendations,
                         stats=stats)
