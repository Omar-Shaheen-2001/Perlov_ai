from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, mail
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

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('البريد الإلكتروني غير صالح', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            try:
                msg = Message(
                    'إعادة تعيين كلمة المرور - PERLOV.ai',
                    recipients=[email],
                    html=f'''
                    <div style="direction: rtl; font-family: Arial, sans-serif;">
                        <h2>مرحباً {user.name}،</h2>
                        <p>لقد طلبت إعادة تعيين كلمة المرور الخاصة بك.</p>
                        <p>يرجى النقر على الرابط أدناه لإعادة تعيين كلمة المرور (صالح لمدة ساعة واحدة):</p>
                        <p><a href="{reset_url}" style="background-color: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">إعادة تعيين كلمة المرور</a></p>
                        <p>أو انسخ والصق الرابط التالي في متصفحك:</p>
                        <p>{reset_url}</p>
                        <p>إذا لم تطلب هذا، فيرجى تجاهل هذا البريد.</p>
                    </div>
                    '''
                )
                mail.send(msg)
                print(f"[EMAIL] Reset email sent to {email}", flush=True)
                flash('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني', 'success')
            except Exception as e:
                print(f"[EMAIL] Error sending email (normal in dev): {e}", flush=True)
                print(f"[EMAIL] Reset link for testing: {reset_url}", flush=True)
                flash('تم إنشاء رابط إعادة التعيين. تحقق من سجلات الخادم للحصول على الرابط (في بيئة الإنتاج، سيتم إرسال بريد)', 'info')
        else:
            flash('إذا كان هذا البريد مسجلاً، سيتم إرسال رابط إعادة التعيين إليه', 'info')
        
        return redirect(url_for('auth.login'))
    
    email = request.args.get('email', '')
    return render_template('auth/forgot_password.html', email=email)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('رابط إعادة التعيين غير صالح أو منتهي الصلاحية', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        if password != confirm_password:
            flash('كلمتا المرور غير متطابقتين', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('تم تعيين كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
