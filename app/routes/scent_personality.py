from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.ai_service import get_ai_response, save_analysis_result
from app.real_products import REAL_PERFUME_PRODUCTS

scent_personality_bp = Blueprint('scent_personality', __name__, url_prefix='/scent-personality')

def recommend_perfume(data):
    """اختر العطر الأنسب بناءً على بيانات الشخصية"""
    basic = data.get('basic', {})
    preferences = data.get('preferences', {})
    emotional = data.get('emotional', {})
    behavioral = data.get('behavioral', {})
    
    gender = basic.get('gender', 'للجنسين')
    personality = basic.get('personality', '')
    strength = preferences.get('strength', '')
    liked_scents = preferences.get('liked_scents', [])
    color = emotional.get('color_preference', '')
    budget = behavioral.get('budget', '')
    
    category_map = {
        'نسائي': 'عطور نسائية',
        'رجالي': 'عطور رجالية',
        'للجنسين': None
    }
    
    price_budget = {
        'اقتصادية': (0, 100),
        'متوسطة': (100, 200),
        'فخمة': (200, 400)
    }
    
    preferred_category = category_map.get(gender)
    budget_range = price_budget.get(budget, (0, 300))
    
    scored_perfumes = []
    
    for idx, perfume in enumerate(REAL_PERFUME_PRODUCTS):
        score = 0
        
        if preferred_category and perfume['category'] == preferred_category:
            score += 20
        elif perfume['category'] == 'عطور يونيسكس':
            score += 10
        
        if perfume['rating'] and perfume['rating'] >= 4.7:
            score += 15
        
        for scent in liked_scents:
            if scent.lower() in perfume['main_notes'].lower():
                score += 10
        
        if color == 'وردي' and any(x in perfume['keywords'] for x in ['نسائي', 'زهري']):
            score += 8
        elif color == 'ذهبي' and any(x in perfume['keywords'] for x in ['عنبري', 'دافئ', 'فاخر']):
            score += 8
        elif color == 'أسود' and any(x in perfume['keywords'] for x in ['غامض', 'قوي', 'شرقي']):
            score += 8
        elif color == 'أخضر' and any(x in perfume['keywords'] for x in ['منعش', 'حمضي']):
            score += 8
        
        price_val = int(perfume['price'].replace('$', '').replace(',', ''))
        if budget_range[0] <= price_val <= budget_range[1]:
            score += 12
        
        if perfume['category'] in ['عطور نسائية', 'عطور رجالية', 'عطور يونيسكس']:
            if score > 0:
                scored_perfumes.append({
                    'index': idx,
                    'score': score,
                    'perfume': perfume
                })
    
    if scored_perfumes:
        scored_perfumes.sort(key=lambda x: x['score'], reverse=True)
        top_perfume = scored_perfumes[0]['perfume']
        return top_perfume
    
    fallback_perfumes = [p for p in REAL_PERFUME_PRODUCTS if preferred_category and p['category'] == preferred_category]
    if fallback_perfumes:
        return max(fallback_perfumes, key=lambda x: x['rating'] if x['rating'] else 0)
    
    return max(REAL_PERFUME_PRODUCTS, key=lambda x: x['rating'] if x['rating'] else 0)

@scent_personality_bp.route('/form')
@login_required
def form():
    return render_template('scent_personality/form.html')

@scent_personality_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    
    basic = data.get('basic', {})
    preferences = data.get('preferences', {})
    environmental = data.get('environmental', {})
    emotional = data.get('emotional', {})
    behavioral = data.get('behavioral', {})
    bio_scent = data.get('bio_scent', {})
    
    # Build comprehensive prompt
    prompt = f"""أنت خبير في بناء الشخصية العطرية وعالم النيقة. حلل البيانات التالية وقدم شخصية عطرية شاملة:

البيانات الأساسية:
- العمر: {basic.get('age', '')}
- الجنس: {basic.get('gender', '')}
- أسلوب الحياة: {basic.get('lifestyle', '')}
- نوع الشخصية: {basic.get('personality', '')}

تفضيلات العطور:
- الروائح المفضلة: {', '.join(preferences.get('liked_scents', []))}
- الروائح المكروهة: {preferences.get('disliked_scents', 'لا توجد')}
- درجة القوة: {preferences.get('strength', '')}
- الثبات المفضل: {preferences.get('longevity', '')}

المدخلات البيئية:
- نوع البشرة: {environmental.get('skin_type', '')}
- حرارة الجسم: {environmental.get('body_temperature', '')}
- المناخ: {environmental.get('climate', '')}
- مناسبات الاستخدام: {', '.join(environmental.get('occasions', []))}

المدخلات النفسية:
- ما يريده من العطر: {', '.join(emotional.get('persona', []))}
- اللون المفضل: {emotional.get('color_preference', '')}
- المشاعر المرتبطة: {', '.join(emotional.get('emotions', []))}
- الروائح التي تثير ذكريات: {emotional.get('positive_memories', 'لا توجد')}

المدخلات السلوكية:
- نمط التفاعل: {behavioral.get('scent_behavior', '')}
- معدل الاستخدام: {behavioral.get('usage_frequency', '')}
- الميزانية: {behavioral.get('budget', '')}
- عطور أحبها: {behavioral.get('liked_perfumes', 'لا توجد')}
- عطور لم تعجبه: {behavioral.get('disliked_perfumes', 'لا توجد')}

Bio-Scent:
- نبرة الصوت: {bio_scent.get('voice_tone', 'لم يتم التحديد')}
- جودة الجلد: {bio_scent.get('skin_quality', 'لم يتم التحديد')}
- الحالة المزاجية: {bio_scent.get('current_mood', 'لم يتم التحديد')}

اكشف:
1. وصف الشخصية العطرية الكامل (3-4 جمل)
2. نقاط القوة العطرية (3-4 نقاط)
3. ألوان العطر المناسبة (RGB تقريبي)
4. Mood Board متكامل (الأجواء، المناسبات، المواسم، الوقت)
5. عبارة هوية شخصية فريدة"""
    
    default_analysis = {
        'personality_description': 'شخصية عطرية متوازنة وجذابة، تجمع بين الأناقة والثقة، مع حس فني عالي في اختيار الروائح',
        'strengths': ['التذوق الرفيع', 'الوعي الشخصي العميق', 'القدرة على التعبير الفني', 'الحساسية للتفاصيل'],
        'scent_colors': {
            'primary': '#0B2E8A',
            'secondary': '#4F7DFF',
            'accent': '#3DDC97'
        },
        'mood_board': {
            'vibes': ['فاخر', 'دافئ', 'غامض', 'مصقول'],
            'occasions': ['سهرات', 'مناسبات خاصة', 'لقاءات مهمة', 'أيام عملية'],
            'seasons': ['خريف', 'شتاء', 'ربيع'],
            'time': 'مساءً وليلاً وأوقات خاصة'
        },
        'identity_statement': 'عطرك هو توقيعك الخاص الذي يسبقك ويبقى بعدك - انعكاس لشخصيتك الفريدة والمصقولة'
    }
    
    try:
        response = get_ai_response(prompt)
        if isinstance(response, dict) and 'personality_description' in response:
            analysis = response
        else:
            analysis = default_analysis
    except:
        analysis = default_analysis
    
    # اختر العطر المقترح
    try:
        recommended = recommend_perfume(data)
        analysis['recommended_perfume'] = recommended
    except:
        analysis['recommended_perfume'] = None
    
    save_analysis_result('scent_personality', data, analysis)
    
    return jsonify({'success': True, 'analysis': analysis})
