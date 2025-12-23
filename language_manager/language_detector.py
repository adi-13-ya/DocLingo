from langdetect import detect, LangDetectException


def detect_language(text):
    """
    Detects language of given text.
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
