"""
Agent Integration for Paper2Slides

Provides LLM-based style transformation for speaker notes.
"""
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


def invoke_style_replicator(text: str, style_profile: str = "bruno") -> str:
    """
    Transform text into narrative style using LLM.

    Args:
        text: Structured text to transform
        style_profile: Style profile (currently only 'bruno' is supported)

    Returns:
        Transformed narrative text

    Raises:
        ValueError: If RAG_LLM_API_KEY environment variable is not set
        Exception: If LLM transformation fails
    """
    logger.warning("Style-replicator agent integration not yet implemented")
    logger.info("Using direct LLM transformation instead...")
    return _transform_via_llm(text, style_profile)


def _transform_via_llm(structured_text: str, style_profile: str) -> str:
    """
    Transform structured notes using LLM API directly.

    Args:
        structured_text: Structured speaker notes to transform
        style_profile: Style profile name ('bruno' or 'generic')

    Returns:
        Narrative text in specified style

    Raises:
        ValueError: If RAG_LLM_API_KEY is not set
        Exception: If API call fails
    """
    api_key = os.getenv("RAG_LLM_API_KEY", "")
    base_url = os.getenv("RAG_LLM_BASE_URL")

    if not api_key:
        raise ValueError(
            "RAG_LLM_API_KEY environment variable is not set. "
            "Please set it to enable LLM-powered narrative transformation."
        )

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    client = OpenAI(**kwargs)

    # Build prompt based on style profile
    if style_profile == "bruno":
        system_prompt = """You are transforming structured speaker notes into a natural, conversational narrative script.

Style guidelines (Bruno's style):
- Conversational and direct, like talking to a friend
- Use "here's the thing" to introduce key points
- Parenthetical asides for extra context or humor
- Self-deprecating humor when appropriate ("Trust me, I've tried...")
- Rhetorical questions to engage audience
- Technical accuracy with accessibility
- Avoid corporate jargon, keep it real

Transform the bullet points into a flowing narrative that sounds like someone actually speaking, not reading from slides."""
    else:
        system_prompt = """You are transforming structured speaker notes into a natural, conversational narrative script.

Make it sound like someone actually speaking to an audience, not reading bullet points.
Keep the content accurate but make the delivery engaging and natural."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": structured_text}
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        narrative = response.choices[0].message.content or ""
        logger.info(f"Generated {len(narrative)} characters of narrative notes")
        return narrative

    except Exception as e:
        logger.exception("LLM transformation failed")
        raise
