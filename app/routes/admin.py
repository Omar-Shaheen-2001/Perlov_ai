import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app import db
from app.models import User, ScentProfile, CustomPerfume, AffiliateProduct, Recommendation

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """حماية المسارات الإدارية - يجب أن يكون المستخدم مصرح ومديراً"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('يجب أن تكون مديراً للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.is_admin and user.check_password(password):
            login_user(user)
            flash('تم الدخول إلى لوحة الإدارة بنجاح', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('بريد أو كلمة مرور غير صحيحة', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    logout_user()
    flash('تم الخروج من لوحة الإدارة', 'success')
    return redirect(url_for('main.index'))

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'users_count': User.query.count(),
        'profiles_count': ScentProfile.query.count(),
        'perfumes_count': CustomPerfume.query.count(),
        'products_count': AffiliateProduct.query.count(),
        'recommendations_count': Recommendation.query.count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_perfumes = CustomPerfume.query.order_by(CustomPerfume.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_perfumes=recent_perfumes)

@admin_bp.route('/users')
@admin_required
def users():
    search_query = request.args.get('search', '').strip()
    
    query = User.query.order_by(User.created_at.desc())
    
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        )
    
    users = query.all()
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'locked_users': User.query.filter_by(is_active=False).count()
    }
    
    return render_template('admin/users.html', users=users, search_query=search_query, stats=stats)

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'تم حذف المستخدم {user.name} بنجاح', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/toggle-lock/<int:id>', methods=['POST'])
@admin_required
def toggle_lock_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك قفل حسابك الخاص', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'فتح' if user.is_active else 'قفل'
    flash(f'تم {action} حساب {user.name} بنجاح', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/view/<int:id>')
@admin_required
def view_user(id):
    user = User.query.get_or_404(id)
    scent_profiles = ScentProfile.query.filter_by(user_id=id).count()
    custom_perfumes = CustomPerfume.query.filter_by(user_id=id).count()
    recommendations = Recommendation.query.filter_by(user_id=id).count()
    
    stats = {
        'scent_profiles': scent_profiles,
        'custom_perfumes': custom_perfumes,
        'recommendations': recommendations
    }
    
    return render_template('admin/user_detail.html', user=user, stats=stats)

@admin_bp.route('/products')
@admin_required
def products():
    products = AffiliateProduct.query.order_by(AffiliateProduct.created_at.desc()).all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        product = AffiliateProduct(
            name=request.form.get('name', ''),
            brand=request.form.get('brand', ''),
            main_notes=request.form.get('main_notes', ''),
            description=request.form.get('description', ''),
            url=request.form.get('url', ''),
            price_text=request.form.get('price_text', ''),
            image_url=request.form.get('image_url', ''),
            gender=request.form.get('gender', ''),
            category=request.form.get('category', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('تمت إضافة المنتج بنجاح', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', product=None)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    product = AffiliateProduct.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name', '')
        product.brand = request.form.get('brand', '')
        product.main_notes = request.form.get('main_notes', '')
        product.description = request.form.get('description', '')
        product.url = request.form.get('url', '')
        product.price_text = request.form.get('price_text', '')
        product.image_url = request.form.get('image_url', '')
        product.gender = request.form.get('gender', '')
        product.category = request.form.get('category', '')
        
        db.session.commit()
        
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', product=product)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    product = AffiliateProduct.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('admin.products'))
