"""
Default Responses - استجابات افتراضية عامة وآمنة
لا تحتوي على أسماء عطور أو علامات تجارية محددة
"""


GENERIC_SCENT_DNA = {
    "scent_personality": "شخصية عطرية متوازنة",
    "personality_description": "شخصية عطرية تتناغم مع طبيعتك الفريدة. يُنصح بإجراء تحليل مفصل للحصول على توصيات دقيقة.",
    "recommended_families": ["عطرية", "خشبية", "زهرية"],
    "ideal_notes": [],
    "notes_to_avoid": [],
    "season_recommendations": "يُنصح باختيار العطور حسب الموسم والمناسبة",
    "overall_analysis": "للحصول على تحليل دقيق، يُرجى تقديم معلومات إضافية عن تفضيلاتك العطرية."
}


GENERIC_CUSTOM_PERFUME = {
    "name": "عطر مخصص",
    "name_meaning": "عطر صُمم خصيصاً لك",
    "top_notes": [],
    "heart_notes": [],
    "base_notes": [],
    "description": "عطر فريد يعكس شخصيتك. يُرجى تقديم تفضيلاتك للحصول على تركيبة مخصصة.",
    "match_score": 0,
    "usage_recommendations": "يُنصح بتجربة العطر على البشرة قبل الاختيار النهائي",
    "longevity": "يعتمد على التركيبة النهائية",
    "sillage": "متوسط",
    "best_seasons": ["جميع الفصول"]
}


GENERIC_RECOMMENDATIONS = {
    "scent_analysis": {
        "top_notes_requested": [],
        "heart_notes_requested": [],
        "base_notes_requested": [],
        "fragrance_family": "غير محدد",
        "fragrance_style": "متنوع",
        "fragrance_character": "شخصي",
        "usage_type": "متعدد الاستخدامات",
        "mood_keywords": ["أنيق", "متوازن"],
        "overall_atmosphere": "مريح",
        "intensity_required": "متوسط"
    },
    "top_3_matches": [],
    "excluded_fragrances": [],
    "dna_summary": "يُرجى تقديم وصف أكثر تفصيلاً للحصول على توصيات دقيقة",
    "scientific_conclusion": "التوصيات تعتمد على المعلومات المتوفرة في قاعدة المعرفة",
    "additional_advice": "للحصول على أفضل النتائج، يُنصح بتجربة العطور على بشرتك الشخصية"
}


GENERIC_FACE_ANALYSIS = {
    "skin_analysis": {
        "skin_type": "متوسطة",
        "skin_tone": "متوسطة",
        "age_range": "غير محدد",
        "perfume_effect": "يعتمد على نوع البشرة",
        "best_concentration": "EDP",
        "longevity_estimate": "يختلف حسب التركيبة"
    },
    "personality_analysis": {
        "personality": "متوازنة",
        "impression": "إيجابي",
        "mood": "هادئ",
        "vibe": "أنيق",
        "style": "Classic"
    },
    "best_families": ["Woody", "Floral", "Fresh"],
    "recommended_perfumes": [],
    "signature_perfume": {
        "name": "يُحدد بناءً على التحليل",
        "reason": "يُرجى إجراء تحليل مفصل"
    },
    "occasion_recommendations": {
        "daily": "عطر خفيف ومنعش",
        "work": "عطر احترافي ومتوازن",
        "evening": "عطر أنيق وجذاب",
        "special": "عطر مميز وفريد"
    }
}


GENERIC_BLEND_PREDICTOR = {
    "blend_name": "مزيج تجريبي",
    "expected_result": "يعتمد على النوتات المختارة",
    "harmony_score": 0,
    "notes_analysis": {
        "top_contribution": "يُحدد بناءً على المكونات",
        "heart_contribution": "يُحدد بناءً على المكونات",
        "base_contribution": "يُحدد بناءً على المكونات"
    },
    "recommendations": ["يُرجى تحديد النوتات للحصول على تحليل دقيق"],
    "warnings": []
}


GENERIC_ARTICLE = {
    "success": True,
    "title": "مقال عن العطور",
    "summary": "مقال يستعرض معلومات متنوعة عن عالم العطور والروائح.",
    "content": """<h2>مقدمة</h2>
<p>عالم العطور عالم واسع ومتنوع يجمع بين الفن والعلم.</p>
<h2>أساسيات العطور</h2>
<p>تتكون العطور من مزيج من النوتات العلوية والوسطى والقاعدية.</p>
<h2>نصائح عامة</h2>
<ul>
<li>اختر العطر الذي يناسب شخصيتك</li>
<li>جرب العطر على بشرتك قبل الشراء</li>
<li>احفظ العطر في مكان بارد وجاف</li>
</ul>""",
    "keywords": "عطور, روائح, نوتات عطرية",
    "suggested_services": []
}


NO_DATA_RESPONSE = {
    "status": "no_data",
    "message": "لم يتم العثور على بيانات كافية لتقديم توصيات محددة.",
    "advice": "يُرجى تقديم معلومات إضافية أو تجربة استعلام مختلف.",
    "general_tips": [
        "استكشف عائلات العطور المختلفة",
        "جرب العطور على بشرتك الشخصية",
        "اختر العطر حسب المناسبة والموسم"
    ]
}


VALIDATION_FAILED_RESPONSE = {
    "status": "validation_failed",
    "message": "لم نتمكن من التحقق من صحة التوصيات.",
    "advice": "نقدم لك نصائح عامة بدلاً من توصيات محددة.",
    "general_guidance": {
        "tip_1": "العطور الخشبية مناسبة للمناسبات الرسمية",
        "tip_2": "العطور الزهرية مثالية للاستخدام اليومي",
        "tip_3": "العطور الشرقية تناسب المساء والمناسبات الخاصة"
    }
}


def get_default_response(module_type: str) -> dict:
    """الحصول على الاستجابة الافتراضية حسب نوع الوحدة"""
    defaults = {
        'scent_dna': GENERIC_SCENT_DNA,
        'custom_perfume': GENERIC_CUSTOM_PERFUME,
        'recommendations': GENERIC_RECOMMENDATIONS,
        'face_analyzer': GENERIC_FACE_ANALYSIS,
        'blend_predictor': GENERIC_BLEND_PREDICTOR,
        'article': GENERIC_ARTICLE,
    }
    return defaults.get(module_type, NO_DATA_RESPONSE).copy()


def get_safe_fallback(module_type: str, error: str = None) -> dict:
    """الحصول على استجابة آمنة عند الفشل"""
    response = VALIDATION_FAILED_RESPONSE.copy()
    if error:
        response['debug_error'] = error
    response['fallback_from'] = module_type
    return response
