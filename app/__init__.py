import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///perlov.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Core blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.scent_dna import scent_dna_bp
    from app.routes.custom_perfume import custom_perfume_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.bio_scent import bio_scent_bp
    
    # New module blueprints
    from app.routes.skin_chemistry import skin_chemistry_bp
    from app.routes.temp_volatility import temp_volatility_bp
    from app.routes.metabolism import metabolism_bp
    from app.routes.climate import climate_bp
    from app.routes.neuroscience import neuroscience_bp
    from app.routes.stability import stability_bp
    from app.routes.predictive import predictive_bp
    from app.routes.scent_personality import scent_personality_bp
    from app.routes.signature import signature_bp
    from app.routes.occasion import occasion_bp
    from app.routes.habit_planner import habit_planner_bp
    from app.routes.digital_twin import digital_twin_bp
    from app.routes.adaptive import adaptive_bp
    from app.routes.oil_mixer import oil_mixer_bp
    from app.routes.marketplace import marketplace_bp
    from app.routes.perfume_blend_predictor import perfume_blend_bp
    from app.routes.articles import articles_bp
    from app.routes.seo import seo_bp
    from app.routes.face_analyzer import face_analyzer_bp
    from app.routes.google_auth import google_auth_bp
    
    # Register core blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(google_auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(scent_dna_bp)
    app.register_blueprint(custom_perfume_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bio_scent_bp)
    
    # Register new module blueprints
    app.register_blueprint(skin_chemistry_bp)
    app.register_blueprint(temp_volatility_bp)
    app.register_blueprint(metabolism_bp)
    app.register_blueprint(climate_bp)
    app.register_blueprint(neuroscience_bp)
    app.register_blueprint(stability_bp)
    app.register_blueprint(predictive_bp)
    app.register_blueprint(scent_personality_bp)
    app.register_blueprint(signature_bp)
    app.register_blueprint(occasion_bp)
    app.register_blueprint(habit_planner_bp)
    app.register_blueprint(digital_twin_bp)
    app.register_blueprint(adaptive_bp)
    app.register_blueprint(oil_mixer_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(perfume_blend_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(face_analyzer_bp)
    
    # Add custom Jinja2 filters
    import json
    @app.template_filter('fromjson')
    def fromjson_filter(value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return []
        return value
    
    @app.template_filter('tojson_safe')
    def tojson_safe_filter(value):
        return json.dumps(value, ensure_ascii=False)
    
    with app.app_context():
        db.create_all()
        # Only seed data if not in production
        if os.environ.get('ENVIRONMENT') != 'production':
            from app.seed_data import seed_admin_user, seed_affiliate_products
            seed_admin_user()
            seed_affiliate_products()
    
    return app
