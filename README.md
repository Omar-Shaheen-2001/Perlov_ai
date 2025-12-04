# PERLOV.ai - منصة العطور الذكية

<div align="center">
  <h3>اصنع عطرك بالذكاء الاصطناعي</h3>
  <p>منصة متكاملة لتحليل الشخصية العطرية وتصميم العطور الشخصية</p>
</div>

## نظرة عامة

PERLOV.ai هي منصة عطور ذكية تعمل بالذكاء الاصطناعي، تقدم:

- **محلل الحمض العطري (Scent DNA Analyzer)**: اكتشف بصمتك العطرية الفريدة
- **مصمم العطور الشخصي (AI Custom Perfume Creator)**: صمم عطرك الخاص
- **توصيات العطور الذكية (AI Scent Recommender)**: احصل على توصيات عطور مع روابط شراء

## التقنيات المستخدمة

### Backend
- Python 3.11
- Flask (Web Framework)
- SQLAlchemy (ORM)
- Flask-Login (Authentication)

### Frontend
- HTML5 + Bootstrap 5 RTL
- CSS3 مع تصميم عصري
- JavaScript (Vanilla)

### Database
- SQLite

### AI Integration
- OpenAI GPT-4o-mini via Replit AI Integrations

## هيكل المشروع

```
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py             # Database models
│   ├── ai_service.py         # OpenAI integration
│   ├── seed_data.py          # Sample affiliate products
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── main.py           # Main pages
│   │   ├── scent_dna.py      # Scent DNA analyzer
│   │   ├── custom_perfume.py # Custom perfume creator
│   │   ├── recommendations.py # AI recommendations
│   │   ├── dashboard.py      # User dashboard
│   │   └── admin.py          # Admin panel
│   ├── templates/            # HTML templates
│   └── static/               # CSS and JS files
├── main.py                   # Application entry point
└── README.md
```

## نماذج البيانات

- **User**: المستخدمين
- **ScentProfile**: بصمات العطور (Scent DNA)
- **CustomPerfume**: العطور المصممة
- **AffiliateProduct**: منتجات الأفلييت
- **Recommendation**: توصيات العطور
- **PrivateLabelProject**: مشاريع العلامات الخاصة

## كيفية التشغيل

1. المشروع جاهز للعمل على Replit مباشرة
2. اضغط على زر "Run" لتشغيل السيرفر
3. ستفتح المنصة على المنفذ 5000

## الصفحات الرئيسية

| الصفحة | الرابط | الوصف |
|--------|--------|-------|
| الرئيسية | `/` | الصفحة الرئيسية |
| الموديولات | `/modules` | اختيار الخدمة |
| حمضك العطري | `/scent-dna` | تحليل البصمة العطرية |
| صمّم عطرك | `/custom-perfume` | تصميم عطر شخصي |
| التوصيات | `/recommendations` | توصيات عطور ذكية |
| لوحة التحكم | `/dashboard` | لوحة المستخدم |
| الإدارة | `/admin` | لوحة الإدارة |

## لوحة الإدارة

- الرابط: `/admin`
- كلمة المرور الافتراضية: `admin123`
- يمكن تغييرها عبر متغير البيئة `ADMIN_PASSWORD`

## الميزات

### للمستخدمين
- تحليل الشخصية العطرية بالذكاء الاصطناعي
- تصميم عطور شخصية فريدة
- توصيات عطور جاهزة للشراء
- حفظ النتائج والوصول إليها لاحقاً
- لوحة تحكم شخصية

### للإدارة
- إدارة المستخدمين
- إدارة منتجات الأفلييت
- إحصائيات المنصة

## ملاحظات تقنية

- المنصة تدعم اللغة العربية مع اتجاه RTL
- تصميم متجاوب يعمل على جميع الأجهزة
- لا يتطلب التسجيل للتجربة الأولية
- البيانات محفوظة في SQLite

## المستقبل

- تصدير التقارير بصيغة PDF
- تكامل مع شبكات الأفلييت الحقيقية
- نظام العلامات الخاصة (Private Label Builder)
- البصمة العطرية الرقمية المتطورة (Digital Scent Twin)

---

<div align="center">
  <p>صنع بـ ❤️ بواسطة PERLOV.ai</p>
</div>
