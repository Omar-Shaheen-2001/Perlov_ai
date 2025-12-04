from app import db
from app.models import User, AffiliateProduct

def seed_admin_user():
    """إنشاء حساب مدير افتراضي"""
    admin = User.query.filter_by(email='admin@perlov.ai').first()
    if not admin:
        admin = User(name='مدير النظام', email='admin@perlov.ai', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ تم إنشاء حساب المدير: admin@perlov.ai")

def seed_affiliate_products():
    if AffiliateProduct.query.first():
        return
    
    products = [
        {
            "name": "Dior Sauvage Eau de Parfum",
            "brand": "Dior",
            "main_notes": "برغموت، فلفل سيشوان، عنبر، فانيلا",
            "description": "عطر رجالي عصري يجسد الحرية والأناقة الجريئة",
            "url": "https://www.dior.com/sauvage",
            "price_text": "$150 - $180",
            "image_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400",
            "gender": "رجالي",
            "category": "شرقي فوجير"
        },
        {
            "name": "Chanel N°5 Eau de Parfum",
            "brand": "Chanel",
            "main_notes": "ألدهيدات، ياسمين، ورد، صندل، فانيلا",
            "description": "العطر الأيقوني الذي يمثل الأناقة الفرنسية الخالدة",
            "url": "https://www.chanel.com/n5",
            "price_text": "$130 - $200",
            "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400",
            "gender": "نسائي",
            "category": "زهري ألدهيدي"
        },
        {
            "name": "Tom Ford Oud Wood",
            "brand": "Tom Ford",
            "main_notes": "عود، خشب الورد، هيل، صندل، فيتيفر",
            "description": "عطر فاخر يمزج بين العود الشرقي والأناقة الغربية",
            "url": "https://www.tomford.com/oud-wood",
            "price_text": "$250 - $350",
            "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
            "gender": "للجنسين",
            "category": "خشبي عودي"
        },
        {
            "name": "Creed Aventus",
            "brand": "Creed",
            "main_notes": "أناناس، بتولا، عنبر، مسك",
            "description": "عطر النجاح والقوة، من أكثر العطور الرجالية شهرة",
            "url": "https://www.creedfragrance.com/aventus",
            "price_text": "$400 - $500",
            "image_url": "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=400",
            "gender": "رجالي",
            "category": "شيبري فاكهي"
        },
        {
            "name": "Yves Saint Laurent Black Opium",
            "brand": "YSL",
            "main_notes": "قهوة، فانيلا، زهر البرتقال، ياسمين",
            "description": "عطر نسائي جريء وأنثوي مع لمسة من الغموض",
            "url": "https://www.ysl.com/black-opium",
            "price_text": "$100 - $150",
            "image_url": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=400",
            "gender": "نسائي",
            "category": "شرقي فانيلي"
        },
        {
            "name": "Maison Francis Kurkdjian Baccarat Rouge 540",
            "brand": "MFK",
            "main_notes": "زعفران، عنبر، خشب الأرز، مسك",
            "description": "عطر فني استثنائي يتميز برائحة كريستالية فريدة",
            "url": "https://www.franciskurkdjian.com/br540",
            "price_text": "$300 - $400",
            "image_url": "https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=400",
            "gender": "للجنسين",
            "category": "شرقي زهري"
        },
        {
            "name": "Versace Eros",
            "brand": "Versace",
            "main_notes": "نعناع، تفاح أخضر، فانيلا، تونكا",
            "description": "عطر رجالي قوي وجذاب مستوحى من الأساطير اليونانية",
            "url": "https://www.versace.com/eros",
            "price_text": "$80 - $120",
            "image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
            "gender": "رجالي",
            "category": "فوجير أروماتي"
        },
        {
            "name": "Jo Malone Wood Sage & Sea Salt",
            "brand": "Jo Malone",
            "main_notes": "ملح البحر، مريمية، جريب فروت",
            "description": "عطر منعش يستحضر نسيم البحر والطبيعة",
            "url": "https://www.jomalone.com/wood-sage",
            "price_text": "$140 - $180",
            "image_url": "https://images.unsplash.com/photo-1595535873420-a599195b3f4a?w=400",
            "gender": "للجنسين",
            "category": "أروماتي بحري"
        },
        {
            "name": "Guerlain Shalimar",
            "brand": "Guerlain",
            "main_notes": "بخور، فانيلا، ورد، ياسمين، أوبوبوناكس",
            "description": "عطر كلاسيكي أسطوري يجسد الأنوثة الشرقية",
            "url": "https://www.guerlain.com/shalimar",
            "price_text": "$100 - $160",
            "image_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400",
            "gender": "نسائي",
            "category": "شرقي بودري"
        },
        {
            "name": "Armani Acqua di Gio Profumo",
            "brand": "Giorgio Armani",
            "main_notes": "برغموت، إيلنغ إيلنغ، باتشولي، عنبر",
            "description": "عطر مائي منعش مع عمق خشبي أنيق",
            "url": "https://www.armani.com/acqua-di-gio",
            "price_text": "$90 - $140",
            "image_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=400",
            "gender": "رجالي",
            "category": "مائي عنبري"
        },
        {
            "name": "Byredo Gypsy Water",
            "brand": "Byredo",
            "main_notes": "صنوبر، ليمون، بخور، صندل، فانيلا",
            "description": "عطر بوهيمي يستحضر روح الحرية والترحال",
            "url": "https://www.byredo.com/gypsy-water",
            "price_text": "$180 - $250",
            "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
            "gender": "للجنسين",
            "category": "خشبي عطري"
        },
        {
            "name": "Lancôme La Vie Est Belle",
            "brand": "Lancôme",
            "main_notes": "سوسن، ياسمين، فانيلا، برالين",
            "description": "عطر يحتفي بجمال الحياة مع حلاوة أنثوية ساحرة",
            "url": "https://www.lancome.com/la-vie-est-belle",
            "price_text": "$85 - $135",
            "image_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400",
            "gender": "نسائي",
            "category": "زهري قرماني"
        }
    ]
    
    for product_data in products:
        product = AffiliateProduct(**product_data)
        db.session.add(product)
    
    db.session.commit()
    print("تم إضافة منتجات الأفلييت التجريبية بنجاح!")
