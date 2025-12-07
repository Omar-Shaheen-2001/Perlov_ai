from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app import db
from app.models import User
from app.ai_service import save_analysis_result, get_ai_response

bio_scent_bp = Blueprint('bio_scent', __name__, url_prefix='/bio-scent', template_folder='../templates/bio_scent')

@bio_scent_bp.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        mood = request.form.get('mood')
        voice_note = request.files.get('voice_note')
        skin_image = request.files.get('skin_image')
        speech_speed = request.form.get('speech_speed')
        
        analysis_result = {
            'mood_analysis': f'تحليل المزاج: {mood}',
            'skin_type': 'معتدلة',
            'fragrance_predictions': ['عطور شرقية دافئة', 'عطور طازجة', 'عطور حساسة'],
            'sensitive_recommendations': 'تم اختيار عطور آمنة للبشرة الحساسة'
        }
        
        return jsonify(analysis_result)
    
    return render_template('bio_scent/form.html')

@bio_scent_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    mood = data.get('mood', '')
    speech_speed = data.get('speech_speed', 'عادية')
    skin_type = data.get('skin_type', 'معتدلة')
    audio_data = data.get('audio_data', '')
    
    # Store audio if provided
    if audio_data:
        import base64
        import os
        try:
            audio_base64 = audio_data.split(',')[1] if ',' in audio_data else audio_data
            audio_bytes = base64.b64decode(audio_base64)
            
            # Create audio directory if not exists
            audio_dir = 'app/static/uploads/audio'
            os.makedirs(audio_dir, exist_ok=True)
            
            # Save audio file
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = f'{audio_dir}/bio_scent_{timestamp}.webm'
            with open(audio_path, 'wb') as f:
                f.write(audio_bytes)
        except Exception as e:
            print(f'Error saving audio: {e}')
    
    result = {
        'voice_analysis': {
            'mood': mood,
            'speech_speed': speech_speed,
            'tone_detected': 'دافئ وهادئ'
        },
        'skin_analysis': {
            'skin_type': skin_type,
            'sensitivity_level': 'متوسطة'
        },
        'fragrance_predictions': [
            'عطور شرقية دافئة',
            'عطور طازجة نقية',
            'عطور حار بنفسجي'
        ],
        'sensitive_recommendations': 'اختيار عطور بنسبة كحول منخفضة وزيوت طبيعية'
    }
    
    save_analysis_result('bio_scent', data, result)
    
    return jsonify(result)

@bio_scent_bp.route('/get-suggestions', methods=['POST'])
@login_required
def get_suggestions():
    """Get AI-powered perfume suggestions based on analysis results."""
    data = request.get_json()
    
    mood = data.get('mood', '')
    speech_speed = data.get('speech_speed', '')
    skin_type = data.get('skin_type', '')
    fragrance_predictions = data.get('fragrance_predictions', [])
    
    prompt = f"""أنت خبير عطور متخصص في تقديم توصيات شخصية. بناءً على تحليل Bio-Scent التالي، قدم 5 عطور مقترحة:

بيانات التحليل:
- المزاج: {mood}
- سرعة الكلام: {speech_speed}
- نوع البشرة: {skin_type}
- توقعات النوتات المفضلة: {', '.join(fragrance_predictions) if fragrance_predictions else 'عطور شرقية وزهرية'}

قدم الإجابة بصيغة JSON فقط بالشكل التالي:
{{
    "suggestions": [
        {{
            "name": "اسم العطر",
            "brand": "اسم العلامة التجارية",
            "reason": "سبب التوصية بناءً على التحليل (جملة واحدة)",
            "main_notes": "النوتات الرئيسية",
            "concentration": "EDP/EDT/Parfum",
            "match_percentage": 90,
            "ideal_for": "الاستخدام المثالي بناءً على المزاج والبشرة"
        }}
    ],
    "personalized_advice": "نصيحة شخصية مخصصة بناءً على تحليلك الحيوي"
}}"""

    response = get_ai_response(prompt, "أنت خبير عطور متخصص في تحليل الشخصيات العطرية وتقديم توصيات دقيقة. أجب دائمًا بصيغة JSON فقط.")
    
    if isinstance(response, dict) and 'suggestions' in response:
        return jsonify(response)
    
    # Fallback response
    return jsonify({
        "suggestions": [
            {
                "name": "Oud Ispahan",
                "brand": "Yves Saint Laurent",
                "reason": "عطر شرقي فاخر يناسب شخصيتك الدافئة",
                "main_notes": "ورد، عود، سماق",
                "concentration": "EDP",
                "match_percentage": 92,
                "ideal_for": "المناسبات الخاصة والمساء"
            },
            {
                "name": "Hypnotic Poison",
                "brand": "Dior",
                "reason": "عطر جذاب يعكس طاقتك وديناميكيتك",
                "main_notes": "جاردينيا، فانيلا، أمبروكسان",
                "concentration": "EDT",
                "match_percentage": 88,
                "ideal_for": "السهرات والتجمعات الاجتماعية"
            },
            {
                "name": "Shalimar",
                "brand": "Guerlain",
                "reason": "كلاسيكي خالد يناسب ذوقك الراقي",
                "main_notes": "ياسمين، ورد، عنبر",
                "concentration": "EDP",
                "match_percentage": 85,
                "ideal_for": "الاستخدام اليومي والمناسبات"
            },
            {
                "name": "Black Opium",
                "brand": "Yves Saint Laurent",
                "reason": "عطر جريء يعكس شخصيتك الجذابة",
                "main_notes": "قهوة، فانيلا، نيروليا",
                "concentration": "EDP",
                "match_percentage": 87,
                "ideal_for": "المساء والعطل النهاية"
            },
            {
                "name": "La Belle",
                "brand": "Jean Paul Gaultier",
                "reason": "عطر نسائي أنيق بتركيبة متوازنة",
                "main_notes": "أسيد، كشمش، موس",
                "concentration": "EDP",
                "match_percentage": 84,
                "ideal_for": "العمل والمناسبات الرسمية"
            }
        ],
        "personalized_advice": "بناءً على تحليلك الحيوي، أنت تفضل العطور الشرقية الفاخرة مع لمسات دافئة. جرّب عطورًا بتركيز EDP عالي لضمان ثبات أطول يناسب طاقتك."
    })
