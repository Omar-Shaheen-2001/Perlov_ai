from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app.models import Article, ArticleComment, ArticleLike
from app import db
import uuid

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')

def get_session_id():
    """Get or create a session identifier for guest users"""
    from flask import session
    if 'guest_id' not in session:
        session['guest_id'] = str(uuid.uuid4())
    return session['guest_id']

@articles_bp.route('/')
def index():
    articles = Article.query.filter_by(is_published=True).order_by(Article.published_at.desc()).all()
    return render_template('articles/index.html', articles=articles)

@articles_bp.route('/<string:slug>')
def view(slug):
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    article.views_count += 1
    db.session.commit()
    
    related_articles = Article.query.filter(
        Article.is_published == True,
        Article.id != article.id,
        Article.topic == article.topic
    ).limit(3).all()
    
    # Check if current user/guest liked this article
    user_liked = False
    if current_user.is_authenticated:
        user_liked = ArticleLike.query.filter_by(article_id=article.id, user_id=current_user.id).first() is not None
    else:
        session_id = get_session_id()
        user_liked = ArticleLike.query.filter_by(article_id=article.id, session_id=session_id).first() is not None
    
    comments = ArticleComment.query.filter_by(article_id=article.id, is_approved=True).order_by(ArticleComment.created_at.desc()).all()
    
    return render_template('articles/view.html', article=article, related_articles=related_articles, comments=comments, user_liked=user_liked)

@articles_bp.route('/<string:slug>/like', methods=['POST'])
def like_article(slug):
    """Like or unlike an article"""
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    if current_user.is_authenticated:
        user_id = current_user.id
        session_id = None
    else:
        user_id = None
        session_id = get_session_id()
    
    # Check if already liked
    existing_like = ArticleLike.query.filter(
        ArticleLike.article_id == article.id,
        (ArticleLike.user_id == user_id) if user_id else (ArticleLike.session_id == session_id)
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        like = ArticleLike(article_id=article.id, user_id=user_id, session_id=session_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    
    if request.is_json:
        return jsonify({'liked': liked, 'likes_count': len(article.likes)})
    
    return redirect(url_for('articles.view', slug=slug))

@articles_bp.route('/<string:slug>/comment', methods=['POST'])
def add_comment(slug):
    """Add a comment to an article"""
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('التعليق لا يمكن أن يكون فارغاً', 'error')
        return redirect(url_for('articles.view', slug=slug))
    
    if len(content) < 3:
        flash('التعليق يجب أن يكون أكثر من 3 أحرف', 'error')
        return redirect(url_for('articles.view', slug=slug))
    
    if len(content) > 1000:
        flash('التعليق لا يمكن أن يتجاوز 1000 حرف', 'error')
        return redirect(url_for('articles.view', slug=slug))
    
    if current_user.is_authenticated:
        user_id = current_user.id
        name = current_user.name
        email = current_user.email
    else:
        user_id = None
        name = request.form.get('name', 'ضيف').strip()
        email = request.form.get('email', '').strip()
    
    comment = ArticleComment(
        article_id=article.id,
        user_id=user_id,
        name=name,
        email=email,
        content=content,
        is_approved=True
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('تم إضافة تعليقك بنجاح', 'success')
    return redirect(url_for('articles.view', slug=slug) + '#comments')

@articles_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (only by comment creator or admin)"""
    comment = ArticleComment.query.get_or_404(comment_id)
    article = comment.article
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('لا يمكنك حذف هذا التعليق', 'error')
        return redirect(url_for('articles.view', slug=article.slug))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('تم حذف التعليق بنجاح', 'success')
    return redirect(url_for('articles.view', slug=article.slug) + '#comments')
