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

## Key Features
- Arabic RTL interface with Bootstrap
- Session-based auth with Flask-Login
- AI-powered scent analysis and perfume creation
- Admin panel for product management

## Running the App
The app runs on port 5000 with `python main.py`

## Admin Access
- URL: `/admin`
- Default password: `admin123` (configurable via ADMIN_PASSWORD env var)

## Recent Changes
- Initial MVP implementation with all core features
- Bootstrap 5 RTL professional design
- OpenAI integration via Replit AI Integrations
