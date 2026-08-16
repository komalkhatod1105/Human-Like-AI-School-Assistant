"""
Multilingual support and language detection.
Handles language detection and provides translations.
"""
import re


class LanguageService:
    """Manages multilingual support and language detection."""

    # Supported languages
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "bn": "Bengali",
        "gu": "Gujarati",
        "pa": "Punjabi",
        "kn": "Kannada",
        "ml": "Malayalam",
        "ur": "Urdu",
    }

    # Language keywords for detection - must be more than English-like keywords
    LANGUAGE_KEYWORDS = {
        "hi": ["namaste", "mera", "baccha", "kya", "kitni", "hai", "batchao", "attendance"],
        "ta": ["vanakkam", "enakku", "enna", "en", "naan"],
        "te": ["namaskaram", "meku", "veedu"],
        "mr": ["namaste", "mala", "baccha", "kay"],
        "bn": ["namaste", "amar", "baccha", "ki"],
        "gu": ["namaste", "mara", "baccha", "su"],
        "pa": ["sat sri akal", "mera", "baccha", "ki"],
        "kn": ["namaskara", "nanna", "maga", "yeno"],
        "ml": ["namaskaram", "ente", "makan", "ethra"],
        "ur": ["assalam", "mera", "baccha", "kya", "hazri"],
    }

    # Response templates in different languages
    RESPONSES = {
        "en": {
            "attendance_student": "{student_name} currently has {attendance}% attendance.",
            "attendance_recent": "{student_name} had {attendance}% attendance last month.",
            "attendance_school": "The current overall school attendance is {attendance}% across {total_students} students.",
            "marked_absent": "{student_name} has been marked absent for today.",
            "marked_present": "{student_name} has been marked present for today.",
            "permission_denied": "You don't have permission to perform this action.",
            "student_not_found": "I couldn't find that student. Could you check the name?",
            "clarify_student": "Sure. Which student should I mark absent?",
            "confirm_action": "Should I mark {student_name} absent for today?",
            "escalation_submitted": "Your call request has been submitted to the {target}. Request ID: {request_id}.",
            "unauthorized": "Sorry, you don't have permission to perform this action.",
            "greeting_student": "Hi! I'm XYZ AI, your school assistant. How can I help you today?",
            "greeting_parent": "Hello! I'm here to help you with your child's school information. How may I support you today?",
            "greeting_teacher": "Hello, teacher. How can I assist with student and class management today?",
            "greeting_principal": "Good day, Principal. I can help with attendance insights and school operations.",
        },
        "hi": {
            "attendance_student": "{student_name} के पास वर्तमान में {attendance}% उपस्थिति है।",
            "attendance_recent": "{student_name} के पास पिछले महीने {attendance}% उपस्थिति थी।",
            "attendance_school": "वर्तमान में {total_students} छात्रों में स्कूल की कुल उपस्थिति {attendance}% है।",
            "marked_absent": "{student_name} को आज के लिए अनुपस्थित अंकित किया गया है।",
            "marked_present": "{student_name} को आज के लिए उपस्थित अंकित किया गया है।",
            "permission_denied": "आपको यह कार्य करने की अनुमति नहीं है।",
            "student_not_found": "मुझे वह छात्र नहीं मिल सका। क्या आप नाम की जांच कर सकते हैं?",
            "clarify_student": "ठीक है। मुझे कौन सा छात्र अनुपस्थित करना चाहिए?",
            "confirm_action": "क्या मुझे {student_name} को आज के लिए अनुपस्थित करना चाहिए?",
            "escalation_submitted": "आपका अनुरोध {target} को भेज दिया गया है। अनुरोध ID: {request_id}।",
            "unauthorized": "खेद है, आपको यह कार्य करने की अनुमति नहीं है।",
            "greeting_student": "नमस्ते! मैं XYZ AI हूँ, आपका स्कूल असिस्टेंट। मैं आपकी कैसे मदद कर सकता हूँ?",
            "greeting_parent": "नमस्ते! मैं आपके बच्चे की स्कूल की जानकारी में आपकी मदद करने के लिए यहाँ हूँ। मैं आपकी कैसे सेवा कर सकता हूँ?",
            "greeting_teacher": "नमस्ते, शिक्षक। मैं छात्र और कक्षा प्रबंधन में आपकी कैसे मदद कर सकता हूँ?",
            "greeting_principal": "नमस्ते प्रिंसिपल। मैं उपस्थिति अंतर्दृष्टि और स्कूल संचालन में मदद कर सकता हूँ।",
        },
        "ta": {
            "attendance_student": "{student_name}க்கு தற்போது {attendance}% கல்விக்கு வருகை உள்ளது.",
            "attendance_recent": "{student_name}க்கு கடந்த மாதம் {attendance}% கல்விக்கு வருகை இருந்தது.",
            "attendance_school": "தற்போது {total_students} மாணவர்களில் பள்ளியின் மொத்த வருகை {attendance}% ஆகும்.",
            "marked_absent": "{student_name} இன்று வருகையிலிருந்து விடுபடுத்தப்பட்டுள்ளார்.",
            "marked_present": "{student_name} இன்று வருகையுறாக குறிப்பிடப்பட்டுள்ளார்.",
            "permission_denied": "இந்த செயலை செய்ய உங்களுக்கு அனுமதி இல்லை.",
            "student_not_found": "அந்த மாணவரை என்னால் கண்டறிய முடியவில்லை. நீங்கள் பெயரை சரிபார்க்க முடியுமா?",
            "clarify_student": "சரி. நான் எந்த மாணவரை வருகை விடுபடுத்த வேண்டும்?",
            "confirm_action": "நான் {student_name}ஐ இன்று வருகையிலிருந்து விடுபடுத்த வேண்டுமா?",
            "escalation_submitted": "உங்கள் அழைப்பு {target}க்கு சமர்ப்பிக்கப்பட்டுள்ளது. அனுரோध ID: {request_id}.",
            "unauthorized": "மன்னிக்கவும், இந்த செயலை செய்ய உங்களுக்கு அனுமதி இல்லை.",
            "greeting_student": "வணக்கம்! நான் XYZ AI, உங்கள் பள்ளி உதவியாளர். இன்று நான் உங்களுக்கு உதவ முடியுமா?",
            "greeting_parent": "வணக்கம்! உங்கள் பிள்ளையின் பள்ளி தகவலில் உங்களுக்கு உதவ நான் இங்கு உள்ளேன். நான் உங்களுக்கு உதவ முடியுமா?",
            "greeting_teacher": "வணக்கம், ஆசிரியர். மாணவர் மற்றும் வகுப்பு நிர்வாகத்தில் நான் உங்களுக்கு உதவ முடியுமா?",
            "greeting_principal": "வணக்கம்校长. வருகை நுண்ணறிவு மற்றும் பள்ளி செயல்பாட்டில் நான் உதவ முடியேன்.",
        },
    }

    def __init__(self):
        """Initialize language service."""
        self.default_language = "en"

    def detect_language(self, message):
        """
        Detect the language of a message.
        Returns: language code
        """
        if not message or not message.strip():
            return self.default_language

        lower = message.lower()

        # Count matches for each language
        lang_scores = {}
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in lower)
            if matches > 0:
                lang_scores[lang] = matches

        # If we have matches and the highest score is >= 2, use that language
        if lang_scores:
            best_lang = max(lang_scores, key=lang_scores.get)
            if lang_scores[best_lang] >= 2:
                return best_lang

        # Default to English
        return self.default_language

    def get_response_template(self, language, key, defaults=None):
        """
        Get a response template for a language.
        Falls back to English if language or key not found.
        """
        if language not in self.RESPONSES:
            language = self.default_language

        templates = self.RESPONSES.get(language, {})
        template = templates.get(key)

        if not template:
            # Fall back to English
            template = self.RESPONSES.get(self.default_language, {}).get(
                key, "{default_text}"
            )

        return template

    def get_supported_languages(self):
        """Get list of supported languages."""
        return self.SUPPORTED_LANGUAGES.copy()

    def format_response(self, language, template_key, **kwargs):
        """
        Format a response in the specified language.
        Uses template_key to find the response template.
        """
        template = self.get_response_template(language, template_key)
        try:
            return template.format(**kwargs)
        except KeyError:
            # If template has missing keys, return template as-is
            return template
