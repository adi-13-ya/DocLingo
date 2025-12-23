from deep_translator import GoogleTranslator
from language_manager.language_detector import detect_language


def translate_text(text, target_lang="en"):
    """
    Translate text to target language if required.
    """
    source_lang = detect_language(text)

    if source_lang == "unknown" or source_lang == target_lang:
        return text, source_lang

    try:
        translated = GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(text)
        return translated, source_lang

    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return text, source_lang
