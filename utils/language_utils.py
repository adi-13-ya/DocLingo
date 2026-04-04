"""
Shared Language Utilities for DocLingo
Centralizes language name mappings used across multiple engines.
"""

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ml": "Malayalam",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "mr": "Marathi",
    "ur": "Urdu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
}


def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name from ISO 639-1 language code.

    Args:
        lang_code: Language code (e.g., "en", "hi", "ml")

    Returns:
        Language name (e.g., "English", "Hindi", "Malayalam")
    """
    return LANGUAGE_NAMES.get(lang_code, lang_code.upper())
