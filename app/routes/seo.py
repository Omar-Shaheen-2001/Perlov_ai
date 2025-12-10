from flask import Blueprint, render_template, Response, url_for
from app.models import Article
from datetime import datetime, timedelta

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/sitemap.xml')
def sitemap():
    """توليد ملف Sitemap تلقائي للمقالات والصفحات الرئيسية"""
    pages = []
    
    # الصفحات الرئيسية
    pages.append({
        'loc': url_for('main.index', _external=True),
        'lastmod': datetime.utcnow().date().isoformat()
    })
    
    pages.append({
        'loc': url_for('articles.index', _external=True),
        'lastmod': datetime.utcnow().date().isoformat()
    })
    
    # المقالات المنشورة
    articles = Article.query.filter_by(is_published=True).all()
    for article in articles:
        pages.append({
            'loc': url_for('articles.view', slug=article.slug, _external=True),
            'lastmod': (article.updated_at or article.published_at or article.created_at).date().isoformat()
        })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    return Response(sitemap_xml, mimetype='application/xml')

@seo_bp.route('/robots.txt')
def robots():
    """ملف robots.txt لتوجيه محركات البحث"""
    robots_txt = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/
Disallow: /static/
Allow: /static/css/
Allow: /static/images/
Allow: /static/js/

Sitemap: https://perlov.ai/sitemap.xml
"""
    return robots_txt, 200, {'Content-Type': 'text/plain'}
