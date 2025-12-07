# PERLOV - منصة محبي العطور

## Overview
PERLOV is a premium perfume discovery platform built with Flask that offers:
- Scent DNA Analysis - Discover your unique fragrance personality
- Custom Perfume Creator - Design personalized perfumes with AI
- AI Recommendations - Get perfume suggestions with affiliate links
- 18 Comprehensive Perfume Analysis Modules

## Tech Stack
- **Backend**: Python 3.11, Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5 RTL, HTML5, CSS3
- **Database**: SQLite
- **AI**: OpenAI via Replit AI Integrations

## Project Structure
```
app/
├── __init__.py         # Flask app factory with all blueprint registrations
├── models.py           # SQLAlchemy models (User, ScentDNA, CustomPerfume, etc.)
├── ai_service.py       # OpenAI integration with get_ai_response helper
├── seed_data.py        # Affiliate product seeds & admin user
├── routes/             # Blueprint routes (18+ modules)
│   ├── auth.py         # Login/Register
│   ├── main.py         # Home & modules
│   ├── admin.py        # Admin dashboard & user management
│   ├── scent_dna.py    # Scent DNA analyzer
│   ├── custom_perfume.py # Custom perfume designer
│   ├── recommendations.py # AI recommendations
│   ├── dashboard.py    # User dashboard
│   ├── bio_scent.py    # Bio-Scent AI analyzer
│   ├── skin_chemistry.py # Skin chemistry match
│   ├── temp_volatility.py # Temperature volatility engine
│   ├── metabolism.py   # Metabolism-based match
│   ├── climate.py      # Climate-based recommendations
│   ├── neuroscience.py # Olfactory neuroscience
│   ├── stability.py    # Stability & diffusion analyzer
│   ├── predictive.py   # Predictive scent engine
│   ├── scent_personality.py # Personality builder
│   ├── signature.py    # Signature scent builder
│   ├── occasion.py     # Occasion-based perfume engine
│   ├── habit_planner.py # Habit-based planner
│   ├── digital_twin.py # Digital scent twin
│   ├── adaptive.py     # Adaptive perfume engine
│   ├── oil_mixer.py    # AI oil & notes mixer
│   └── marketplace.py  # Scent marketplace
├── templates/          # Jinja2 HTML templates (18+ module templates)
└── static/
    ├── css/style.css   # Luxury styling
    └── images/         # Assets (logos, etc)
main.py                 # Entry point
```

## Design System

### Royal Blue Color Palette
- **Primary** (#0B2E8A) - أزرق ملكي - Header, buttons, main actions
- **Dark** (#071F5E) - أزرق داكن - Footer, gradients
- **Light** (#4F7DFF) - أزرق فاتح - Hover states, accents
- **Background** (#FFFFFF) - أبيض نقي - Page backgrounds
- **Light Gray** (#F2F4F8) - رمادي فاتح - Cards, sections
- **Dark Text** (#1C1C1C) - رمادي داكن - Main text
- **Success** (#3DDC97) - أخضر - Positive actions, confirmation
- **Error** (#FF4D4F) - أحمر - Warnings, errors

### Typography
- **Arabic**: Cairo (300-800 weight) - عصرية، تقنية، أناقة
- **English**: Poppins (300-800 weight) - Modern, clean, professional

### Design Elements
- Clean, minimal design with spacious layouts
- 12-20px rounded corners for modern feel
- Primary gradient: linear-gradient(135deg, #0B2E8A, #071F5E)
- Light shadows with blue tint (rgba(11, 46, 138, 0.08))
- Smooth hover animations & transitions
- White cards with subtle borders
- Line icons for modern aesthetic

### Brand Personality
- **النبرة**: عاطفية – راقية – ذكية
- **الأسلوب**: Minimal – Clean
- **الجمهور**: فئة شبابية + مستخدمي التقنية
- **الشعور**: Trust + Love + Innovation

## 18 Perfume Analysis Modules

### Core Services
1. **Scent DNA** (/scent-dna) - Discover unique fragrance personality
2. **Custom Perfume** (/custom-perfume) - AI-designed personalized perfumes
3. **AI Recommendations** (/recommendations) - Perfume suggestions with affiliate links

### Biological Analysis
4. **Bio-Scent AI** (/bio-scent) - Voice, skin, mood analysis
5. **Skin Chemistry** (/skin-chemistry) - Perfume-skin compatibility
6. **Temperature Volatility** (/temp-volatility) - Body heat & perfume evaporation
7. **Metabolism Match** (/metabolism) - Activity-based recommendations

### Environmental & Psychological
8. **Climate Engine** (/climate) - Weather-based suggestions
9. **Neuroscience** (/neuroscience) - Memory & emotion-scent connections
10. **Stability Analyzer** (/stability) - Longevity & sillage measurement

### AI Advanced Features
11. **Predictive Engine** (/predictive) - Future perfume predictions
12. **Scent Personality** (/scent-personality) - Complete fragrance identity
13. **Signature Builder** (/signature) - Create your signature scent

### Planning & Organization
14. **Occasion Matcher** (/occasion) - Event-based recommendations
15. **Habit Planner** (/habit-planner) - Weekly/monthly perfume schedules
16. **Adaptive Engine** (/adaptive) - Real-time recommendations

### Digital & Creative
17. **Digital Twin** (/digital-twin) - Permanent digital scent identity
18. **Oil Mixer** (/oil-mixer) - Custom note blending
19. **Marketplace** (/marketplace) - Real products from verified stores with AI-powered search

## Key Features Implemented

### User Management System
- **User Management Page** (/admin/users):
  - Search by name or email with live filtering
  - View user statistics (total, active, locked users)
  - Lock/unlock user accounts with mandatory reason tracking
  - Delete users with confirmation dialog
  - View detailed user profiles with activity stats (Scent DNA, Perfumes, Recommendations)
- Lock reason displayed to locked users on login
- Account status toggle with is_active field
- User detail page shows comprehensive activity statistics

### Admin Panel
- **Dashboard**: Stats (Users, Profiles, Perfumes, Products)
- **User Management**: Search, lock/unlock, delete, view details
- **Affiliate Product Management**: CRUD operations
- **Luxury-themed cards and tables**
- **Secure admin authentication** (email + password)
- **Auto-seeded admin account** on app startup (admin@perlov.ai / admin123)

### Authentication & Security
- Session-based auth with Flask-Login
- Locked user prevention with lock reason display
- Password hashing with werkzeug
- Admin-only route protection

### Frontend
- **RTL Arabic Interface** with Bootstrap 5
- **Responsive Design** for all devices
- **Hero Section** with tagline: "PERLOV منصة محبي العطور"
- **Feature Cards** for all 18 modules organized by category
- **Luxury Footer** with links and copyright

## Running the App
```bash
python main.py
# App runs on http://0.0.0.0:5000
```

## Admin Access
- **URL**: `/admin`
- **Default Credentials**: admin@perlov.ai / admin123
- **Password Configuration**: Via ADMIN_PASSWORD env var

## Deployment
- **Target**: Autoscale
- **Run Command**: `python main.py`
- **Port**: 0.0.0.0:5000 (required for Autoscale)
- **Health Check**: / endpoint returns 200 immediately
- **Database**: Seeding only in development (not production)

## Recent Changes (Dec 5, 2025)
- **Real Marketplace Implementation**:
  - 45+ real products from verified stores (Sephora, FragranceNet, FragranceX, Notino, Macy's, etc.)
  - 6 product categories: عطور نسائية, رجالية, يونيسكس, زيوت, نوتات, عبوات
  - AI-powered search with hybrid approach (curated database + AI suggestions)
  - Accurate data source tracking (curated_database, ai_suggestions, or mixed)
  - All products include real purchase URLs from verified international stores
- Fixed mobile navbar-toggler icon color (Velvet Plum instead of white)
- Added 18 comprehensive perfume analysis modules
- Created 15 new route files with robust AI fallbacks
- Created 15 new template directories with forms
- Updated modules.html with categorized grid layout
- Added get_ai_response() helper to ai_service.py
- All modules have default fallback data for reliability
- Changed brand name from "PERLOV.ai" to "PERLOV"
- Updated tagline to "منصة محبي العطور" (Perfume Lovers Platform)
- Logo integration setup (custom logo in navbar)
- Deployment configuration validated and working

## User Preferences
- Arabic-first design with RTL support
- Luxury feminine aesthetic throughout
- Exact hex color palette adherence
- Modern, clean typography choices
