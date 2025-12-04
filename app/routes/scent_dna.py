import uuid
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user
from app import db
from app.models import ScentProfile
from app.ai_service import generate_scent_dna_analysis

scent_dna_bp = Blueprint('scent_dna', __name__)

@scent_dna_bp.route('/scent-dna', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        gender = request.form.get('gender', '')
        age_range = request.form.get('age_range', '')
        personality_type = request.form.get('personality_type', '')
        favorite_notes = request.form.getlist('favorite_notes')
        disliked_notes = request.form.getlist('disliked_notes')
        climate = request.form.get('climate', '')
        skin_type = request.form.get('skin_type', '')
        
        profile_data = {
            'gender': gender,
            'age_range': age_range,
            'personality_type': personality_type,
            'favorite_notes': ', '.join(favorite_notes),
            'disliked_notes': ', '.join(disliked_notes),
            'climate': climate,
            'skin_type': skin_type
        }
        
        ai_result = generate_scent_dna_analysis(profile_data)
        
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        scent_profile = ScentProfile(
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session_id,
            gender=gender,
            age_range=age_range,
            personality_type=personality_type,
            favorite_notes=', '.join(favorite_notes),
            disliked_notes=', '.join(disliked_notes),
            climate=climate,
            skin_type=skin_type,
            scent_personality=ai_result.get('scent_personality', ''),
            ai_analysis=json.dumps(ai_result, ensure_ascii=False)
        )
        
        db.session.add(scent_profile)
        db.session.commit()
        
        flash('تم تحليل بصمتك العطرية بنجاح!', 'success')
        return redirect(url_for('scent_dna.result', id=scent_profile.id))
    
    return render_template('scent_dna/form.html')

@scent_dna_bp.route('/scent-dna/result/<int:id>')
def result(id):
    scent_profile = ScentProfile.query.get_or_404(id)
    
    session_id = session.get('session_id')
    if not current_user.is_authenticated:
        if scent_profile.session_id != session_id:
            flash('غير مصرح لك بعرض هذه النتيجة', 'error')
            return redirect(url_for('main.index'))
    elif scent_profile.user_id and scent_profile.user_id != current_user.id:
        if not current_user.is_admin:
            flash('غير مصرح لك بعرض هذه النتيجة', 'error')
            return redirect(url_for('main.index'))
    
    try:
        ai_analysis = json.loads(scent_profile.ai_analysis) if scent_profile.ai_analysis else {}
    except:
        ai_analysis = {}
    
    return render_template('scent_dna/result.html', profile=scent_profile, analysis=ai_analysis)
