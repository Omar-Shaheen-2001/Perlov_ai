from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    lock_reason = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scent_profiles = db.relationship('ScentProfile', backref='user', lazy=True)
    custom_perfumes = db.relationship('CustomPerfume', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    private_label_projects = db.relationship('PrivateLabelProject', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
