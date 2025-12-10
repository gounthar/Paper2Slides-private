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
- Conversational and direct, like talking to a friend over coffee
- Varied conversational hooks - mix it up! Examples:
  * "So, [topic]..."
  * "Look, [statement]..."
  * "Okay, [topic]..."
  * "Let me tell you about [topic]..."
  * "You know what's interesting? [statement]..."
  * Direct statements without preamble when appropriate
- Parenthetical asides for extra context, technical details, or humor (these work great!)
- Self-deprecating humor when appropriate ("Trust me, I've been there...")
- Rhetorical questions to engage audience ("Why does this matter?", "What's the catch?")
- Mix short punchy sentences with longer explanatory ones
- Use "honestly", "actually", "basically" sparingly - not every sentence
- Technical accuracy with accessibility - explain like you would to a smart colleague
- Avoid corporate jargon, keep it real and authentic
- Vary your rhythm - don't start every paragraph the same way

IMPORTANT: Don't overuse any single pattern. If you used "here's the thing" or "look" or "okay" recently, pick a different opening. Natural speakers vary their patterns!

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
