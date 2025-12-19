from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    lock_reason = db.Column(db.String(500), nullable=True)
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    verification_token = db.Column(db.String(256), nullable=True)
    verification_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scent_profiles = db.relationship('ScentProfile', backref='user', lazy=True)
    custom_perfumes = db.relationship('CustomPerfume', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    private_label_projects = db.relationship('PrivateLabelProject', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        token = secrets.token_urlsafe(32)
        self.reset_token = token
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def verify_reset_token(self, token):
        if self.reset_token != token or not self.reset_token_expiry:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None
    
    def generate_verification_token(self):
        token = secrets.token_urlsafe(32)
        self.verification_token = token
        self.verification_token_expiry = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def verify_email(self, token):
        if self.verification_token != token or not self.verification_token_expiry:
            return False
        if datetime.utcnow() > self.verification_token_expiry:
            return False
        self.email_verified = True
        self.verification_token = None
        self.verification_token_expiry = None
        return True

class ScentProfile(db.Model):
    __tablename__ = 'scent_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20))
    age_range = db.Column(db.String(20))
    personality_type = db.Column(db.String(100))
    favorite_notes = db.Column(db.Text)
    disliked_notes = db.Column(db.Text)
    climate = db.Column(db.String(50))
    skin_type = db.Column(db.String(20))
    ai_analysis = db.Column(db.Text)
    scent_personality = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    custom_perfumes = db.relationship('CustomPerfume', backref='scent_profile', lazy=True)

class CustomPerfume(db.Model):
    __tablename__ = 'custom_perfumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    scent_profile_id = db.Column(db.Integer, db.ForeignKey('scent_profiles.id'), nullable=True)
    name = db.Column(db.String(100))
    top_notes = db.Column(db.Text)
    heart_notes = db.Column(db.Text)
    base_notes = db.Column(db.Text)
    description = db.Column(db.Text)
    match_score = db.Column(db.Float, default=0.0)
    usage_recommendations = db.Column(db.Text)
    occasion = db.Column(db.String(50))
    intensity = db.Column(db.String(20))
    budget = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AffiliateProduct(db.Model):
    __tablename__ = 'affiliate_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    main_notes = db.Column(db.Text)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    price_text = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    gender = db.Column(db.String(20))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    scent_profile_id = db.Column(db.Integer, db.ForeignKey('scent_profiles.id'), nullable=True)
    query_text = db.Column(db.Text)
    recommendations_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PrivateLabelProject(db.Model):
    __tablename__ = 'private_label_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    brand_name = db.Column(db.String(100))
    target_audience = db.Column(db.String(200))
    num_scents = db.Column(db.Integer, default=3)
    style = db.Column(db.String(50))
    ai_report = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_type = db.Column(db.String(50), nullable=False)
    module_name_ar = db.Column(db.String(100), nullable=False)
    module_icon = db.Column(db.String(50), default='bi-star')
    input_data = db.Column(db.Text)
    result_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('analysis_results', lazy=True))

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content_ar = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=True)
    summary_ar = db.Column(db.String(500), nullable=False)
    summary_en = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    topic = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.Text, nullable=True)
    suggested_services = db.Column(db.Text, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    views_count = db.Column(db.Integer, default=0)
    
    creator = db.relationship('User', backref=db.backref('articles', lazy=True), foreign_keys=[created_by])
    comments = db.relationship('ArticleComment', backref='article', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('ArticleLike', backref='article', lazy=True, cascade='all, delete-orphan')

class ArticleComment(db.Model):
    __tablename__ = 'article_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('article_comments', lazy=True))

class ArticleLike(db.Model):
    __tablename__ = 'article_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('article_likes', lazy=True))


class PerfumeNote(db.Model):
    """نموذج النوتات العطرية لنظام RAG"""
    __tablename__ = 'perfume_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False, unique=True)
    name_ar = db.Column(db.String(100), nullable=False)
    family = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    volatility = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.Text, nullable=False)
    works_well_with = db.Column(db.Text)
    avoid_with = db.Column(db.Text)
    best_for = db.Column(db.Text)
    concentration = db.Column(db.String(50))
    origin = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """تحويل النوتة إلى قاموس للاستخدام في RAG"""
        import json
        
        def safe_parse_json_list(value):
            """Safely parse JSON list, handling malformed data"""
            if not value:
                return []
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [item.strip() for item in str(value).split(',') if item.strip()]
        
        return {
            'id': self.id,
            'note': self.name_en,
            'arabic': self.name_ar,
            'family': self.family,
            'role': self.role,
            'volatility': self.volatility,
            'profile': self.profile,
            'works_well_with': safe_parse_json_list(self.works_well_with),
            'avoid_with': safe_parse_json_list(self.avoid_with),
            'best_for': safe_parse_json_list(self.best_for),
            'concentration': self.concentration or '',
            'origin': self.origin or ''
        }
    
    @staticmethod
    def get_active_notes():
        """جلب جميع النوتات الفعّالة"""
        return PerfumeNote.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_all_notes_as_dict():
        """جلب جميع النوتات الفعّالة كقائمة قواميس"""
        notes = PerfumeNote.get_active_notes()
        return [note.to_dict() for note in notes]
