import uuid
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user
from app import db
from app.models import ScentProfile, CustomPerfume, AffiliateProduct
from app.ai_service import generate_custom_perfume

custom_perfume_bp = Blueprint('custom_perfume', __name__)

@custom_perfume_bp.route('/custom-perfume', methods=['GET', 'POST'])
def form():
    scent_profile_id = request.args.get('scent_profile_id', type=int)
    scent_profile = None
    
    if scent_profile_id:
        scent_profile = ScentProfile.query.get(scent_profile_id)
    
    if request.method == 'POST':
        occasion = request.form.get('occasion', '')
        intensity = request.form.get('intensity', '')
        budget = request.form.get('budget', '')
        scent_profile_id = request.form.get('scent_profile_id', type=int)
        
        if scent_profile_id:
            scent_profile = ScentProfile.query.get(scent_profile_id)
        
        perfume_data = {
            'occasion': occasion,
            'intensity': intensity,
            'budget': budget
        }
        
        ai_result = generate_custom_perfume(perfume_data, scent_profile)
        
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        top_notes = ai_result.get('top_notes', [])
        heart_notes = ai_result.get('heart_notes', [])
        base_notes = ai_result.get('base_notes', [])
        
        ai_details = {
            'name_meaning': ai_result.get('name_meaning', ''),
            'longevity': ai_result.get('longevity', ''),
            'sillage': ai_result.get('sillage', ''),
            'best_seasons': ai_result.get('best_seasons', []),
            'usage_recommendations': ai_result.get('usage_recommendations', '')
        }
        
        custom_perfume = CustomPerfume(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session_id,
            scent_profile_id=scent_profile_id,
            name=ai_result.get('name', 'عطر مخصص'),
            top_notes=', '.join(top_notes) if isinstance(top_notes, list) else str(top_notes),
            heart_notes=', '.join(heart_notes) if isinstance(heart_notes, list) else str(heart_notes),
            base_notes=', '.join(base_notes) if isinstance(base_notes, list) else str(base_notes),
            description=ai_result.get('description', ''),
            match_score=float(ai_result.get('match_score', 85)),
            usage_recommendations=json.dumps(ai_details, ensure_ascii=False),
            occasion=occasion,
            intensity=intensity,
            budget=budget
        )
        
        db.session.add(custom_perfume)
        db.session.commit()
        
        flash('تم تصميم عطرك الشخصي بنجاح!', 'success')
        return redirect(url_for('custom_perfume.result', id=custom_perfume.id))
    
    return render_template('custom_perfume/form.html', scent_profile=scent_profile)

@custom_perfume_bp.route('/custom-perfume/result/<int:id>')
def result(id):
    perfume = CustomPerfume.query.get_or_404(id)
    
    session_id = session.get('session_id')
    if not current_user.is_authenticated:
        if perfume.session_id != session_id:
            flash('غير مصرح لك بعرض هذه النتيجة', 'error')
            return redirect(url_for('main.index'))
    elif perfume.user_id and perfume.user_id != current_user.id:
        if not current_user.is_admin:
            flash('غير مصرح لك بعرض هذه النتيجة', 'error')
            return redirect(url_for('main.index'))
    
    try:
        ai_details = json.loads(perfume.usage_recommendations) if perfume.usage_recommendations else {}
    except:
        ai_details = {}
    
    similar_products = AffiliateProduct.query.limit(4).all()
    
    return render_template('custom_perfume/result.html', perfume=perfume, details=ai_details, similar_products=similar_products)
