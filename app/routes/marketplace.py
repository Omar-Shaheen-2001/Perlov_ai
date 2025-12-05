from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/')
@login_required
def index():
    return render_template('marketplace/index.html')

@marketplace_bp.route('/search', methods=['POST'])
@login_required
def search():
    data = request.get_json()
    
    category = data.get('category', '')
    price_range = data.get('price_range', '')
    concentration = data.get('concentration', '')
    
    products = [
        {
            'name': 'زيت العود الكمبودي',
            'category': 'زيوت',
            'price': '$120',
            'concentration': 'نقي 100%',
            'description': 'زيت عود فاخر من كمبوديا',
            'link': '#'
        },
        {
            'name': 'زيت الورد الدمشقي',
            'category': 'زيوت',
            'price': '$85',
            'concentration': 'نقي 100%',
            'description': 'أجود أنواع زيت الورد',
            'link': '#'
        },
        {
            'name': 'مسك أبيض طبيعي',
            'category': 'نوتات',
            'price': '$45',
            'concentration': 'مركز',
            'description': 'مسك طبيعي بدون كحول',
            'link': '#'
        },
        {
            'name': 'عنبر أصلي',
            'category': 'نوتات',
            'price': '$150',
            'concentration': 'نقي',
            'description': 'عنبر حوتي أصلي',
            'link': '#'
        },
        {
            'name': 'زجاجة عطر فاخرة 50مل',
            'category': 'عبوات',
            'price': '$25',
            'concentration': 'N/A',
            'description': 'زجاجة كريستال مع بخاخ',
            'link': '#'
        },
        {
            'name': 'خشب الصندل الهندي',
            'category': 'نوتات',
            'price': '$95',
            'concentration': 'نقي 100%',
            'description': 'زيت صندل ميسور الأصلي',
            'link': '#'
        }
    ]
    
    if category:
        products = [p for p in products if p['category'] == category]
    
    return jsonify({
        'success': True,
        'products': products,
        'total': len(products)
    })
