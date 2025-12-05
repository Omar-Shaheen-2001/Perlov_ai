from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.real_products import search_products, get_featured_products, REAL_PERFUME_PRODUCTS
from app.ai_service import search_real_perfume_products

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/')
@login_required
def index():
    featured = get_featured_products(6)
    return render_template('marketplace/index.html', featured_products=featured)

@marketplace_bp.route('/search', methods=['POST'])
@login_required
def search():
    data = request.get_json()
    
    search_query = data.get('query', '').strip()
    category = data.get('category', 'all')
    price_range = data.get('price_range', 'all')
    use_ai = data.get('use_ai', False)
    
    curated_products = search_products(search_query, category, price_range)
    curated_count = len(curated_products)
    products = curated_products.copy()
    data_source = 'curated_database'
    
    if search_query and (use_ai or curated_count < 3):
        try:
            db_product_names = [p['name'].lower() for p in curated_products]
            ai_result = search_real_perfume_products(search_query, category, price_range)
            
            if ai_result and ai_result.get('products'):
                ai_products = []
                for ai_product in ai_result['products']:
                    if ai_product.get('name', '').lower() not in db_product_names:
                        if ai_product.get('store_url') and ai_product['store_url'].startswith('http'):
                            ai_products.append(ai_product)
                
                if ai_products:
                    products = curated_products + ai_products[:4]
                    if curated_count == 0:
                        data_source = 'ai_suggestions'
                    else:
                        data_source = 'curated_database+ai_suggestions'
        except Exception as e:
            pass
    
    if not products:
        return jsonify({
            'success': True,
            'products': [],
            'total': 0,
            'search_summary': 'لم يتم العثور على منتجات مطابقة - جرب كلمات بحث مختلفة',
            'data_source': data_source
        })
    
    summary_parts = [f'تم العثور على {len(products)} منتج']
    if search_query:
        summary_parts.append(f'لـ "{search_query}"')
    if category and category != 'all':
        summary_parts.append(f'في فئة {category}')
    if price_range and price_range != 'all':
        price_labels = {'budget': 'اقتصادي', 'mid': 'متوسط', 'luxury': 'فاخر'}
        summary_parts.append(f'- {price_labels.get(price_range, price_range)}')
    
    if 'ai' in data_source:
        summary_parts.append('- منتجات حقيقية + اقتراحات ذكية')
    else:
        summary_parts.append('- منتجات حقيقية من متاجر موثوقة')
    
    return jsonify({
        'success': True,
        'products': products[:12],
        'total': len(products),
        'search_summary': ' '.join(summary_parts),
        'data_source': data_source
    })

@marketplace_bp.route('/ai-search', methods=['POST'])
@login_required
def ai_search():
    """AI-powered product discovery for specific searches."""
    data = request.get_json()
    
    search_query = data.get('query', '').strip()
    category = data.get('category', 'all')
    price_range = data.get('price_range', 'all')
    
    if not search_query:
        return jsonify({
            'success': False,
            'error': 'يرجى إدخال كلمات البحث'
        }), 400
    
    try:
        result = search_real_perfume_products(search_query, category, price_range)
        
        if result and result.get('products'):
            valid_products = []
            for p in result['products']:
                if p.get('store_url') and p['store_url'].startswith('http'):
                    valid_products.append(p)
            
            return jsonify({
                'success': True,
                'products': valid_products[:8],
                'total': len(valid_products),
                'search_summary': f'اقتراحات ذكية لـ "{search_query}"',
                'data_source': 'ai_suggestions'
            })
        
        return jsonify({
            'success': True,
            'products': [],
            'total': 0,
            'search_summary': 'لم يتم العثور على اقتراحات',
            'data_source': 'ai_suggestions'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في البحث الذكي',
            'data_source': 'error'
        }), 500

@marketplace_bp.route('/product/<int:index>')
@login_required
def product_detail(index):
    if 0 <= index < len(REAL_PERFUME_PRODUCTS):
        product = REAL_PERFUME_PRODUCTS[index]
        return jsonify({'success': True, 'product': product})
    return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404
