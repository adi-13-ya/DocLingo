from utils.llm_client import chat_completion
from language_manager.translation_manager import translate_text


def generate_explanation(chunks, translation_path, query, query_language="en"):
    """
    Generates:
    1. LLM-based human-readable explanation (same language as query)
    2. Structured explanation metadata (for console/logs)
    """

    # -----------------------------
    # 1. Structured metadata (console only)
    # -----------------------------
    explanation_meta = {
        "chunks_used": len(chunks),
        "translation_strategy": translation_path,
        "grounded": True,
        "explanation_type": "llm_rationale"
    }

    # -----------------------------
    # 2. No chunks → fixed explanation
    # -----------------------------
    if not chunks:
        explanation_text_en = (
            "The system could not find any part of the document that answers your question."
        )

        explanation_text, _ = translate_text(
            explanation_text_en,
            target_lang=query_language
        )

        return explanation_text, explanation_meta

    # -----------------------------
    # 3. Prepare context for LLM
    # -----------------------------
    context_text = "\n\n".join(
        [f"Section {i+1}: {chunk}" for i, chunk in enumerate(chunks)]
    )

    system_prompt = (
        "You are an explanation generator for a document-based AI system.\n"
        "Your task is to explain WHY the provided sections of the document were used "
        "to answer the user's question.\n\n"
        "Rules:\n"
        "- Do NOT answer the question again\n"
        "- Do NOT add new information\n"
        "- Do NOT use outside knowledge\n"
        "- Explain only based on the given document sections\n"
        "- Keep the explanation short and clear (2–3 sentences)"
    )

    user_prompt = f"""
User Question:
{query}

Document Sections Used:
{context_text}

Explain briefly why these sections were selected to answer the question.
"""

    # -----------------------------
    # 4. LLM call (controlled)
    # -----------------------------
    response = chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )

    explanation_text_en = response.choices[0].message.content.strip()

    # -----------------------------
    # 5. Translate explanation to query language
    # -----------------------------
    explanation_text, _ = translate_text(
        explanation_text_en,
        target_lang=query_language
    )

    return explanation_text, explanation_meta
