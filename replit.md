# PERLOV.ai - AI Perfume Platform

## Overview
PERLOV.ai is an AI-powered perfume platform built with Flask that offers:
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
├── models.py           # SQLAlchemy models
├── ai_service.py       # OpenAI integration
├── seed_data.py        # Affiliate product seeds
├── routes/             # All route blueprints
├── templates/          # Jinja2 templates
└── static/css/         # Stylesheets
main.py                 # Entry point
```

## Design System (Updated Dec 4, 2025)

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

### Key Features
- Arabic RTL interface with Bootstrap 5
- Session-based auth with Flask-Login
- AI-powered scent analysis and perfume creation
- Admin panel for product management
- Luxury feminine aesthetic throughout

## Running the App
The app runs on port 5000 with `python main.py`

## Admin Access
- URL: `/admin`
- Default password: `admin123` (configurable via ADMIN_PASSWORD env var)

## Recent Changes
- **Dec 4, 2025 (Latest)**: User Management System & Dashboard Enhancements
  - **User Management Page** (/admin/users):
    - Search by name or email with live filtering
    - View user statistics (total, active, locked users)
    - Lock/unlock user accounts (toggle is_active status)
    - Delete users with confirmation dialog
    - View detailed user profiles with activity stats (Scent DNA, Perfumes, Recommendations)
  - Added `is_active` field to User model for account status
  - User detail page shows comprehensive user activity statistics
  - Dashboard improvements: Redesigned Scent DNA card with luxury styling
  - Fixed stat-card colors for better contrast and luxury appearance
  - Enhanced footer with luxury gradient styling and hover effects
  - Module card button styling: Added gold gradient for recommendations
  
- **Dec 4, 2025**: Complete design system overhaul with exact luxury color palette
  - Updated CSS with new color variables and gradients
  - Redesigned admin dashboard stat-cards with luxury gradients
  - All cards, forms, buttons styled with new palette
  - Pearl Mist card for light contrast on dashboards
  - Enhanced glassmorphic effects and shadows

## Admin Panel Features
- **Dashboard**: Stats (Users, Profiles, Perfumes, Products)
- **User Management** (/admin/users):
  - Search users by name or email
  - View quick stats: total users, active users, locked users
  - Lock/unlock accounts to disable/enable user access
  - Delete users with confirmation
  - View user detail page with activity statistics
- **Affiliate Product Management**: CRUD operations with luxury styling
- Luxury-themed cards and tables
- Secure email + password authentication
- Auto-seeded admin account on app startup (admin@perlov.ai / admin123)

