import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app import db
from app.models import User, ScentProfile, CustomPerfume, AffiliateProduct, Recommendation, Article, PerfumeNote
from app.ai_service import generate_article
import json
from datetime import datetime
import re
import requests
import threading

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
    all_users = User.query.all()
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'locked_users': User.query.filter_by(is_active=False).count()
    }
    
    return render_template('admin/users.html', users=users, all_users=all_users, search_query=search_query, stats=stats)

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
    
    if user.is_active:
        user.is_active = False
        user.lock_reason = request.form.get('lock_reason', 'تم قفل الحساب من قبل المسؤول')
        action = 'قفل'
    else:
        user.is_active = True
        user.lock_reason = None
        action = 'فتح'
    
    db.session.commit()
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

@admin_bp.route('/articles')
@admin_required
def articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles_list.html', articles=articles)

@admin_bp.route('/articles/create', methods=['GET', 'POST'])
@admin_required
def create_article():
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        keywords = request.form.get('keywords', '').strip()
        tone = request.form.get('tone', 'إعلامي متوازن').strip()
        
        if not topic:
            flash('يجب إدخال موضوع المقال', 'error')
            return render_template('admin/article_generator.html')
        
        ai_result = generate_article(topic, keywords, tone)
        
        if not ai_result.get('success'):
            flash(f'خطأ في توليد المقال: {ai_result.get("error")}', 'error')
            return render_template('admin/article_generator.html')
        
        slug = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '-').lower()
        slug = slug[:50]
        
        import json
        suggested_services = json.dumps(ai_result.get('suggested_services', []), ensure_ascii=False)
        
        article = Article(
            title_ar=ai_result['title'],
            slug=slug,
            content_ar=ai_result['content'],
            summary_ar=ai_result['summary'],
            topic=topic,
            keywords=ai_result['keywords'],
            suggested_services=suggested_services,
            is_published=True,
            published_at=datetime.utcnow(),
            created_by=current_user.id
        )
        
        db.session.add(article)
        db.session.commit()
        
        # إرسال المقال للفهرسة بشكل غير متزامن
        threading.Thread(target=ping_indexnow, args=(article,), daemon=True).start()
        
        flash('تم إنشاء ونشر المقال بنجاح!', 'success')
        return redirect(url_for('admin.articles'))
    
    return render_template('admin/article_generator.html')

@admin_bp.route('/articles/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    
    if request.method == 'POST':
        article.title_ar = request.form.get('title_ar', '').strip()
        article.content_ar = request.form.get('content_ar', '').strip()
        article.summary_ar = request.form.get('summary_ar', '').strip()
        article.topic = request.form.get('topic', '').strip()
        article.keywords = request.form.get('keywords', '').strip()
        article.image_url = request.form.get('image_url', '').strip()
        
        db.session.commit()
        flash('تم تحديث المقال بنجاح', 'success')
    
    return render_template('admin/article_edit.html', article=article)

def ping_indexnow(article):
    """إرسال المقال إلى IndexNow API للفهرسة السريعة"""
    try:
        article_url = url_for('articles.view', slug=article.slug, _external=True)
        
        # إرسال إلى IndexNow API (Bing/Google)
        indexnow_data = {
            "host": "perlov.ai",  # استبدل باسم نطاقك الفعلي
            "key": os.getenv('INDEXNOW_KEY', ''),
            "keyLocation": "https://perlov.ai/indexnow-key.txt",
            "urlList": [article_url]
        }
        
        # محاولة الإرسال (بدون توقف العملية إذا فشلت)
        if indexnow_data['key']:
            requests.post(
                "https://api.indexnow.org/indexnow",
                json=indexnow_data,
                timeout=5
            )
    except Exception as e:
        # تسجيل الخطأ دون توقف النشر
        print(f"IndexNow error: {str(e)}")

@admin_bp.route('/articles/publish/<int:id>', methods=['POST'])
@admin_required
def publish_article(id):
    article = Article.query.get_or_404(id)
    article.is_published = True
    article.published_at = datetime.utcnow()
    db.session.commit()
    
    # إرسال المقال للفهرسة بشكل غير متزامن
    threading.Thread(target=ping_indexnow, args=(article,), daemon=True).start()
    
    flash(f'تم نشر المقال "{article.title_ar}" بنجاح', 'success')
    return redirect(url_for('admin.articles'))

@admin_bp.route('/articles/unpublish/<int:id>', methods=['POST'])
@admin_required
def unpublish_article(id):
    article = Article.query.get_or_404(id)
    article.is_published = False
    db.session.commit()
    
    flash(f'تم إلغاء نشر المقال "{article.title_ar}"', 'success')
    return redirect(url_for('admin.articles'))

@admin_bp.route('/articles/delete/<int:id>', methods=['POST'])
@admin_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    title = article.title_ar
    db.session.delete(article)
    db.session.commit()
    
    flash(f'تم حذف المقال "{title}" بنجاح', 'success')
    return redirect(url_for('admin.articles'))


@admin_bp.route('/notes')
@admin_required
def notes():
    """عرض جميع النوتات العطرية"""
    search_query = request.args.get('search', '').strip()
    family_filter = request.args.get('family', '').strip()
    
    query = PerfumeNote.query.order_by(PerfumeNote.name_en.asc())
    
    if search_query:
        query = query.filter(
            (PerfumeNote.name_en.ilike(f'%{search_query}%')) |
            (PerfumeNote.name_ar.ilike(f'%{search_query}%'))
        )
    
    if family_filter:
        query = query.filter(PerfumeNote.family == family_filter)
    
    notes_list = query.all()
    
    families = db.session.query(PerfumeNote.family).distinct().all()
    families = [f[0] for f in families]
    
    stats = {
        'total': PerfumeNote.query.count(),
        'active': PerfumeNote.query.filter_by(is_active=True).count(),
        'inactive': PerfumeNote.query.filter_by(is_active=False).count(),
        'families': len(families)
    }
    
    return render_template('admin/notes.html', 
                         notes=notes_list, 
                         stats=stats, 
                         families=families,
                         search_query=search_query,
                         family_filter=family_filter)


def parse_list_input(value):
    """Convert comma-separated or JSON input to JSON string"""
    if not value or not value.strip():
        return '[]'
    
    value = value.strip()
    
    if value.startswith('[') and value.endswith(']'):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
    
    items = [item.strip().strip('"\'') for item in value.split(',') if item.strip()]
    return json.dumps(items, ensure_ascii=False)


@admin_bp.route('/notes/add', methods=['GET', 'POST'])
@admin_required
def add_note():
    """إضافة نوتة جديدة"""
    if request.method == 'POST':
        try:
            note = PerfumeNote(
                name_en=request.form.get('name_en', '').strip(),
                name_ar=request.form.get('name_ar', '').strip(),
                family=request.form.get('family', ''),
                role=request.form.get('role', ''),
                volatility=request.form.get('volatility', ''),
                profile=request.form.get('profile', '').strip(),
                works_well_with=parse_list_input(request.form.get('works_well_with', '')),
                avoid_with=parse_list_input(request.form.get('avoid_with', '')),
                best_for=parse_list_input(request.form.get('best_for', '')),
                concentration=request.form.get('concentration', '').strip(),
                origin=request.form.get('origin', '').strip(),
                is_active='is_active' in request.form
            )
            db.session.add(note)
            db.session.commit()
            flash(f'تم إضافة النوتة "{note.name_en}" بنجاح', 'success')
            return redirect(url_for('admin.notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة النوتة: {str(e)}', 'error')
    
    return render_template('admin/note_form.html', note=None)


@admin_bp.route('/notes/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_note(id):
    """تعديل نوتة"""
    note = PerfumeNote.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            note.name_en = request.form.get('name_en', '').strip()
            note.name_ar = request.form.get('name_ar', '').strip()
            note.family = request.form.get('family', '')
            note.role = request.form.get('role', '')
            note.volatility = request.form.get('volatility', '')
            note.profile = request.form.get('profile', '').strip()
            note.works_well_with = parse_list_input(request.form.get('works_well_with', ''))
            note.avoid_with = parse_list_input(request.form.get('avoid_with', ''))
            note.best_for = parse_list_input(request.form.get('best_for', ''))
            note.concentration = request.form.get('concentration', '').strip()
            note.origin = request.form.get('origin', '').strip()
            note.is_active = 'is_active' in request.form
            
            db.session.commit()
            flash(f'تم تحديث النوتة "{note.name_en}" بنجاح', 'success')
            return redirect(url_for('admin.notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تحديث النوتة: {str(e)}', 'error')
    
    return render_template('admin/note_form.html', note=note)


@admin_bp.route('/notes/toggle/<int:id>', methods=['POST'])
@admin_required
def toggle_note(id):
    """تفعيل/تعطيل نوتة"""
    note = PerfumeNote.query.get_or_404(id)
    note.is_active = not note.is_active
    db.session.commit()
    
    status = 'تفعيل' if note.is_active else 'تعطيل'
    flash(f'تم {status} النوتة "{note.name_en}"', 'success')
    return redirect(url_for('admin.notes'))


@admin_bp.route('/notes/delete/<int:id>', methods=['POST'])
@admin_required
def delete_note(id):
    """حذف نوتة"""
    note = PerfumeNote.query.get_or_404(id)
    name = note.name_en
    db.session.delete(note)
    db.session.commit()
    
    flash(f'تم حذف النوتة "{name}" بنجاح', 'success')
    return redirect(url_for('admin.notes'))


@admin_bp.route('/notes/rebuild-index', methods=['POST'])
@admin_required
def rebuild_rag_index():
    """إعادة بناء فهرس FAISS من قاعدة البيانات"""
    try:
        from app.rag_builder import rebuild_faiss_index
        
        result = rebuild_faiss_index()
        
        if result['success']:
            flash(f'تم إعادة بناء الفهرس بنجاح! ({result["notes_count"]} نوتة)', 'success')
        else:
            flash(f'خطأ في إعادة بناء الفهرس: {result["error"]}', 'error')
    except Exception as e:
        flash(f'خطأ: {str(e)}', 'error')
    
    return redirect(url_for('admin.notes'))


@admin_bp.route('/notes/migrate-json', methods=['POST'])
@admin_required
def migrate_notes_from_json():
    """نقل النوتات من ملف JSON إلى قاعدة البيانات"""
    try:
        import json
        
        with open('notes_kb.json', 'r', encoding='utf-8') as f:
            notes_data = json.load(f)
        
        imported = 0
        skipped = 0
        
        for note_data in notes_data:
            existing = PerfumeNote.query.filter_by(name_en=note_data['note']).first()
            if existing:
                skipped += 1
                continue
            
            note = PerfumeNote(
                name_en=note_data['note'],
                name_ar=note_data['arabic'],
                family=note_data['family'],
                role=note_data['role'],
                volatility=note_data['volatility'],
                profile=note_data['profile'],
                works_well_with=json.dumps(note_data.get('works_well_with', []), ensure_ascii=False),
                avoid_with=json.dumps(note_data.get('avoid_with', []), ensure_ascii=False),
                best_for=json.dumps(note_data.get('best_for', []), ensure_ascii=False),
                concentration=note_data.get('concentration', ''),
                origin=note_data.get('origin', ''),
                is_active=True
            )
            db.session.add(note)
            imported += 1
        
        db.session.commit()
        flash(f'تم استيراد {imported} نوتة بنجاح ({skipped} موجودة مسبقاً)', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في الاستيراد: {str(e)}', 'error')
    
    return redirect(url_for('admin.notes'))
