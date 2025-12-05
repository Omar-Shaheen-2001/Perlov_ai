# PERLOV - منصة محبي العطور

## Overview
PERLOV is a premium perfume discovery platform built with Flask that offers:
- Scent DNA Analysis - Discover your unique fragrance personality
- Custom Perfume Creator - Design personalized perfumes with AI
- AI Recommendations - Get perfume suggestions with affiliate links

## Tech Stack
- **Backend**: Python 3.11, Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5 RTL, HTML5, CSS3
- **Database**: SQLite
- **AI**: OpenAI via Replit AI Integrations

## Project Structure
```
app/
├── __init__.py         # Flask app factory
├── models.py           # SQLAlchemy models (User, ScentDNA, CustomPerfume, etc.)
├── ai_service.py       # OpenAI integration
├── seed_data.py        # Affiliate product seeds & admin user
├── routes/             # Blueprint routes
│   ├── auth.py         # Login/Register
│   ├── main.py         # Home & modules
│   ├── admin.py        # Admin dashboard & user management
│   ├── scent_dna.py    # Scent DNA analyzer
│   ├── custom_perfume.py # Custom perfume designer
│   ├── recommendations.py # AI recommendations
│   └── dashboard.py    # User dashboard
├── templates/          # Jinja2 HTML templates
└── static/
    ├── css/style.css   # Luxury styling
    └── images/         # Assets (logos, etc)
main.py                 # Entry point
```

## Design System

### Luxury Color Palette
- **Blush Rose** (#E9C9D3) - Primary feminine accent
- **Pearl Mist** (#F7F4F6) - Clean, elegant backgrounds
- **Velvet Plum** (#B37A94) - Primary buttons & actions
- **Warm Amber** (#D9A35F) - Secondary warmth & luxury accents
- **Soft Musk White** (#FDF9F7) - Premium backgrounds
- **Deep Charcoal** (#1F1F1F) - Text & sophistication

### Typography
- **Arabic**: Cairo (300-500 weight) - elegant, modern, light
- **English**: Playfair Display (headings) + Poppins (body) - luxury serif aesthetic

### Design Elements
- Glassmorphism with backdrop blur effects
- 25-30px rounded corners for luxury feel
- Soft gradients (Rose→Amber, Rose→Pearl, Amber→Rose)
- Subtle shadows with color-matched opacity
- Smooth hover animations & transitions

## Key Features Implemented

### User Management System (Latest)
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
- **Feature Cards** for modules (Scent DNA, Custom Perfume, Recommendations)
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
- Changed brand name from "PERLOV.ai" to "PERLOV"
- Updated tagline to "منصة محبي العطور" (Perfume Lovers Platform)
- All PERLOV.ai references changed to PERLOV throughout app
- Logo integration setup (custom logo in navbar)
- Page title and footer updated with new branding
- Deployment configuration validated and working

## User Preferences
- Arabic-first design with RTL support
- Luxury feminine aesthetic throughout
- Exact hex color palette adherence
- Modern, clean typography choices
