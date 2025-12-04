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
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.scent_dna import scent_dna_bp
    from app.routes.custom_perfume import custom_perfume_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(scent_dna_bp)
    app.register_blueprint(custom_perfume_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    with app.app_context():
        db.create_all()
        from app.seed_data import seed_admin_user, seed_affiliate_products
        seed_admin_user()
        seed_affiliate_products()
    
    return app
