import uuid
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user
from app import db
from app.models import ScentProfile, Recommendation, AffiliateProduct
from app.ai_service import generate_recommendations

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations', methods=['GET', 'POST'])
def index():
    recommendations_data = None
    products = AffiliateProduct.query.all()
    
    scent_profile = None
    if current_user.is_authenticated:
        scent_profile = ScentProfile.query.filter_by(user_id=current_user.id).order_by(ScentProfile.created_at.desc()).first()
    else:
        session_id = session.get('session_id')
        if session_id:
            scent_profile = ScentProfile.query.filter_by(session_id=session_id).order_by(ScentProfile.created_at.desc()).first()
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        
        if not query:
            flash('يرجى إدخال وصف لما تبحث عنه', 'error')
        else:
            ai_result = generate_recommendations(query, scent_profile, products)
            
            session_id = session.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['session_id'] = session_id
            
            recommendation = Recommendation(
                user_id=current_user.id if current_user.is_authenticated else None,
                session_id=session_id,
                scent_profile_id=scent_profile.id if scent_profile else None,
                query_text=query,
                recommendations_json=json.dumps(ai_result, ensure_ascii=False)
            )
            
            db.session.add(recommendation)
            db.session.commit()
            
            recommendations_data = ai_result
            flash('تم إنشاء التوصيات بنجاح!', 'success')
    
    return render_template('recommendations/index.html', 
                         recommendations=recommendations_data, 
                         products=products,
                         has_profile=scent_profile is not None)
