# PERLOV - منصة محبي العطور

## Overview
PERLOV is a premium Flask-based perfume discovery platform offering Scent DNA Analysis, Custom Perfume Creation with AI, and AI-powered recommendations with affiliate links. It aims to provide a personalized fragrance journey for users through advanced AI and biological/environmental analysis, catering to a tech-savvy youth audience with a luxurious and innovative experience.

## User Preferences
- Arabic-first design with RTL support
- Luxury feminine aesthetic throughout
- Exact hex color palette adherence
- Modern, clean typography choices

## System Architecture

### UI/UX Decisions
- **Color Palette**: Royal Blue theme (Primary: #0B2E8A, Dark: #071F5E, Light: #4F7DFF, Background: #FFFFFF, Light Gray: #F2F4F8, Dark Text: #1C1C1C, Success: #3DDC97, Error: #FF4D4F).
- **Typography**: Arabic: Cairo (300-800 weight), English: Poppins (300-800 weight) for a modern, elegant, and clean feel.
- **Design Elements**: Clean, minimal design with spacious layouts, 12-20px rounded corners, primary gradient (linear-gradient(135deg, #0B2E8A, #071F5E)), light shadows with blue tint, smooth hover animations, white cards with subtle borders, and line icons.
- **Brand Personality**: Emotional, sophisticated, intelligent, with a minimal and clean style targeting a youthful, tech-oriented audience, evoking trust, love, and innovation.
- **Localization**: Multi-language support (Arabic, English, Hindi, Persian) with RTL as default and smooth transitions.

### Technical Implementations
- **Backend**: Python 3.11, Flask, SQLAlchemy, Flask-Login.
- **Frontend**: Bootstrap 5 RTL, HTML5, CSS3.
- **Database**: SQLite.
- **AI Integration**: OpenAI via Replit AI Integrations.
- **Core Features**:
    - **Scent DNA Analysis**: Discover unique fragrance personality.
    - **Custom Perfume Creator**: AI-designed personalized perfumes.
    - **AI Recommendations**: Perfume suggestions with affiliate links based on advanced DNA-focused matching.
    - **20 Comprehensive Perfume Analysis Modules**: Including Bio-Scent AI, Skin Chemistry, Climate Engine, Neuroscience, Predictive Engine, Signature Scent Builder, Occasion Matcher, Perfume Blend Predictor™, and the new AI Face Scent Analyzer™.
    - **User Management System**: Admin panel for user search, lock/unlock, deletion, and activity tracking.
    - **Authentication & Security**: Session-based auth with Flask-Login, password hashing, and admin-only route protection.
    - **Marketplace**: Features 45+ real products across 6 categories with AI-powered search and direct purchase links.

### Feature Specifications
- **Scent DNA Analysis**: Dual-mode analysis system:
    - **Primary Mode (RAG-Based)**: Uses FAISS vector search to extract notes from knowledge base (minimum 3+ notes). Enforces strict adherence to KB with no hallucination.
    - **Fallback Mode (AI General)**: When KB has insufficient data (<3 notes), switches to AI expertise mode allowing general fragrance knowledge.
    - **Mode Tracking**: Each result includes `_mode` (kb_primary/ai_general/fallback_safe) and `_kb_source` flag for transparency.
    - **Data Points**: Analyzes gender, age range, personality type, preferred/disliked notes, climate, and skin type to generate scent personality, family recommendations, ideal notes, and seasonal guidance.
- **Perfume Blend Predictor™**: AI-powered system predicting blend results from user inputs (perfume names, concentrations, blend ratio, goal, skin type, environment) and providing comprehensive results like expected scent, suggested name, harmony analysis, and recommendations.
- **Expert-Level Precision Recommendations**: DNA-first scent matching system using 8 strict criteria focusing on fragrance DNA (style, character, family, usage, mood, atmosphere) and a 6-factor analysis for highly compatible suggestions and scientific exclusion lists.
- **Enhanced Bio-Scent Module**: AI-powered suggestions based on mood, speech speed, skin type, and fragrance predictions, returning personalized perfume suggestions.
- **Enhanced Skin Chemistry Module**: Precise AI-driven analysis based on expanded inputs (skin type, sensitivity, body temperature, oily/dry areas, past reactions, preferences) to provide suitable perfumes, stability analysis, chemical considerations, and application tips.
- **AI-Powered Article Generator**: Admin system for creating professional fragrance articles with AI assistance. Admins input topic, keywords, and tone → AI generates complete article with title, summary, and detailed content → Admin can edit and publish → Articles appear in public articles section visible to all users with dedicated articles page in navbar.
- **AI Face Scent Analyzer™**: Advanced facial analysis module using OpenAI Vision API. Features: upload/camera image capture, skin type detection (dry/oily/combination/sensitive), skin tone analysis, age range estimation, personality mapping from facial features (mood, vibe, style), facial geometry analysis. Returns: best fragrance families, top 5 personalized perfume recommendations with match scores, signature perfume selection, and occasion-based recommendations (daily/work/evening/special).
- **Database-Managed RAG System**: Complete RAG (Retrieval Augmented Generation) system using FAISS vector search for intelligent fragrance note retrieval. Features:
    - **PerfumeNote Model**: Database table with 15 fields (name_en, name_ar, family, role, volatility, profile, works_well_with, avoid_with, best_for, concentration, origin, incense_style, intensity_weight, formality_score, is_active).
    - **Admin CRUD Interface**: Full management at `/admin/notes` - add, edit, toggle, delete notes with search and family filtering.
    - **Smart Bulk Import with AI Analysis & Deduplication**: `/admin/notes/bulk-import` - Add notes via text field. AI automatically analyzes input with detailed instructions (accurate family classification, role determination, volatility assessment, unique names enforcement). Advanced duplicate detection: exact match prevention + fuzzy matching (70%+ similarity detection) to prevent adding similar notes.
    - **Dynamic FAISS Index**: Hash-based embeddings (MD5 + numpy, 384 dimensions) stored in `app/data/notes.index`.
    - **Rebuild Button**: Admin can click "إعادة بناء الفهرس" to regenerate FAISS index from active database notes.
    - **RAG Context Injection**: Automatically injects relevant notes into all AI prompts (Scent DNA, Custom Perfume, Articles, Face Analyzer).
    - **Cache System**: `app/data/notes_cache.json` provides fast access with database fallback.

## Recent Changes (Dec 20, 2025)
- Fixed template bug: corrected display of `notes_to_avoid` in Scent DNA results from looping through characters to displaying as plain text in warning box.
- Added Bulk Import feature for perfume notes: New `/admin/notes/bulk-import` route with AI-powered text analysis that automatically extracts and organizes notes by family.
- New `analyze_perfume_notes_bulk_import()` function in `ai_service.py` handles automated note data extraction from free-form text input with highly detailed analysis instructions.
- New `find_similar_notes()` function implements fuzzy matching (SequenceMatcher) to detect similar notes and prevent duplicates.
- Enhanced admin bulk import route to check both exact duplicates and similar notes (70%+ threshold), with detailed feedback to users about skipped entries.
- Improved AI prompt with detailed instructions for accurate fragrance classification, role assignment, and volatility assessment.
- Updated admin notes interface with new "استيراد نوتات" (Import Notes) button and modal with comprehensive usage instructions.

## External Dependencies
- **OpenAI**: For AI functionalities including scent DNA analysis, custom perfume creation, recommendations, various module analyses, and automated note bulk import with detailed analysis.
- **SQLAlchemy**: ORM for database interactions.
- **Flask-Login**: For user session management and authentication.
- **Bootstrap 5 RTL**: Frontend framework for responsive and RTL-enabled design.
- **werkzeug**: For password hashing in authentication.
- **difflib**: Python standard library for fuzzy string matching in duplicate detection.
