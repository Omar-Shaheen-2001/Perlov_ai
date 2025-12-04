from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('عذراً، تم قفل حسابك.', 'error')
                if user.lock_reason:
                    flash(f'السبب: {user.lock_reason}', 'info')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(next_page if next_page else url_for('dashboard.index'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        if not name or len(name) < 2:
            errors.append('الاسم يجب أن يكون على الأقل حرفين')
        
        try:
            validate_email(email)
        except EmailNotValidError:
            errors.append('البريد الإلكتروني غير صالح')
        
        if len(password) < 6:
            errors.append('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
        
        if password != confirm_password:
            errors.append('كلمتا المرور غير متطابقتين')
        
        if User.query.filter_by(email=email).first():
            errors.append('البريد الإلكتروني مسجل مسبقاً')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('تم إنشاء الحساب بنجاح! مرحباً بك في PERLOV.ai', 'success')
            return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('main.index'))
