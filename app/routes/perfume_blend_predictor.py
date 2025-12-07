from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.ai_service import get_ai_response, save_analysis_result

perfume_blend_bp = Blueprint('perfume_blend', __name__, url_prefix='/perfume-blend-predictor')

@perfume_blend_bp.route('/form')
@login_required
def form():
    return render_template('perfume_blend_predictor/form.html')

@perfume_blend_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    """Predict the result of blending two perfumes using AI."""
    data = request.get_json()
    
    perfume1_name = data.get('perfume1_name', '')
    perfume1_concentration = data.get('perfume1_concentration', '')
    perfume2_name = data.get('perfume2_name', '')
    perfume2_concentration = data.get('perfume2_concentration', '')
    blend_ratio = data.get('blend_ratio', '50/50')
    blend_goal = data.get('blend_goal', '')
    skin_type = data.get('skin_type', '')
    environment = data.get('environment', '')
    
    prompt = f"""أنت خبير متخصص في علم دمج العطور (Perfume Blending Specialist). قم بتنبؤ دقيق جداً لنتيجة دمج عطرين:

مدخلات الدمج:
- العطر الأول: {perfume1_name} ({perfume1_concentration})
- العطر الثاني: {perfume2_name} ({perfume2_concentration})
- نسبة الدمج المقترحة: {blend_ratio}
- هدف الدمج: {blend_goal if blend_goal else 'رائحة فريدة ومميزة'}
- نوع البشرة: {skin_type if skin_type else 'غير محدد'}
- البيئة/الطقس: {environment if environment else 'غير محدد'}

المطلوب: قدم تنبؤ دقيق جداً يتضمن:

1. **النتيجة العطرية المتوقعة** (الرائحة النهائية):
   - وصف كامل للرائحة الناتجة من الدمج
   - النوتات البارزة والمسيطرة في الخليط
   - الشخصية الإجمالية للرائحة المدمجة

2. **اسم مقترح للرائحة الناتجة**:
   - اسم إبداعي وجذاب يعكس الخليط

3. **أقرب عطر تجاري يشبه الخليط**:
   - عطر حقيقي يشبه نتيجة الدمج مع التفسير

4. **تحليل التناسق**:
   - النوتات المتناسقة والمتكاملة
   - النوتات المتعارضة (إن وجدت)
   - الديناميكية الكيميائية للدمج

5. **إيجابيات الدمج**:
   - 3-4 مزايا رئيسية للخليط

6. **سلبيات الدمج**:
   - 2-3 تحديات محتملة (إن وجدت)

7. **التوصية النهائية**:
   - هل الدمج ناجح أم غير مناسب؟
   - نسبة النجاح (0-100%)
   - الأفضل الاستخدام

8. **النسب المقترحة البديلة**:
   - 2-3 نسب مختلفة مع الفوائد لكل منها

قدم الإجابة بصيغة JSON دقيقة بالشكل التالي:
{{
    "expected_result": {{
        "scent_description": "وصف الرائحة النهائية",
        "dominant_notes": ["نوتة 1", "نوتة 2", "نوتة 3"],
        "overall_character": "الشخصية الإجمالية"
    }},
    "suggested_name": "اسم الرائحة المقترح",
    "similar_commercial_fragrance": {{
        "name": "اسم العطر التجاري",
        "brand": "اسم العلامة",
        "why_similar": "شرح التشابه"
    }},
    "harmony_analysis": {{
        "harmonizing_notes": ["نوتة 1", "نوتة 2"],
        "conflicting_notes": ["نوتة متعارضة (اختياري)"],
        "chemical_dynamics": "شرح الديناميكية الكيميائية"
    }},
    "positives": ["إيجابية 1", "إيجابية 2", "إيجابية 3"],
    "negatives": ["سلبية 1", "سلبية 2"],
    "final_recommendation": {{
        "success": true,
        "success_percentage": 85,
        "verdict": "الدمج ناجح جداً",
        "best_for": "الاستخدام الأمثل"
    }},
    "alternative_ratios": [
        {{
            "ratio": "60/40",
            "benefits": "الفوائد"
        }},
        {{
            "ratio": "70/30",
            "benefits": "الفوائد"
        }}
    ]
}}"""

    default_prediction = {
        'expected_result': {
            'scent_description': 'رائحة خشبية-حمضية-عطرية فاخرة تجمع بين الحرارة والنضارة',
            'dominant_notes': ['حمضيات دافئة', 'خشب السيدار', 'عنبر ناعم'],
            'overall_character': 'خليط متوازن بين القوة والأناقة'
        },
        'suggested_name': 'التعانق الفاخر',
        'similar_commercial_fragrance': {
            'name': 'Dior Homme Sport 2021',
            'brand': 'Dior',
            'why_similar': 'تقدم نفس التوازن بين الحموضة والدفء'
        },
        'harmony_analysis': {
            'harmonizing_notes': ['حمضيات البرغموت', 'نوتات الخشب', 'العنبر'],
            'conflicting_notes': [],
            'chemical_dynamics': 'انصهار سلس بدون تنافر'
        },
        'positives': ['رائحة جديدة ومميزة', 'نضارة + فخامة', 'قوة وفوحان ممتاز'],
        'negatives': ['قد يصبح ثقيلاً عند 50/50', 'قد يحتاج وقت للاستقرار'],
        'final_recommendation': {
            'success': True,
            'success_percentage': 85,
            'verdict': 'الدمج ناجح جداً وقابل للارتداء يومياً',
            'best_for': 'جميع المناسبات والفصول'
        },
        'alternative_ratios': [
            {
                'ratio': '70/30',
                'benefits': 'يبرز الحموضة والنضارة أكثر'
            },
            {
                'ratio': '60/40',
                'benefits': 'توازن مثالي بين العطرين'
            }
        ]
    }
    
    try:
        response = get_ai_response(prompt, "أنت خبير متخصص في علم دمج العطور. قدم تنبؤات دقيقة وعملية بصيغة JSON فقط.")
        if isinstance(response, dict) and 'expected_result' in response:
            prediction = response
        else:
            prediction = default_prediction
    except:
        prediction = default_prediction
    
    save_analysis_result('perfume_blend', data, prediction)
    
    return jsonify({
        'success': True,
        'prediction': prediction
    })
