from flask import Blueprint, render_template
from app.models import Article

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')

@articles_bp.route('/')
def index():
    articles = Article.query.filter_by(is_published=True).order_by(Article.published_at.desc()).all()
    return render_template('articles/index.html', articles=articles)

@articles_bp.route('/<string:slug>')
def view(slug):
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    article.views_count += 1
    from app import db
    db.session.commit()
    
    related_articles = Article.query.filter(
        Article.is_published == True,
        Article.id != article.id,
        Article.topic == article.topic
    ).limit(3).all()
    
    return render_template('articles/view.html', article=article, related_articles=related_articles)
