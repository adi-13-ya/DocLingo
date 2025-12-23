def compute_confidence(num_chunks, translation_strategy):
    """
    Computes confidence based on retrieval & translation.
    """
    score = 0.0

    if num_chunks >= 3:
        score += 0.5
    elif num_chunks == 2:
        score += 0.3
    elif num_chunks == 1:
        score += 0.15

    if translation_strategy == "none":
        score += 0.3
    elif translation_strategy == "partial":
        score += 0.2
    elif translation_strategy == "full":
        score += 0.1

    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    return "Low"
