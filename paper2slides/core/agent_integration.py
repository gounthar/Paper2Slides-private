"""
Agent Integration for Paper2Slides

Provides LLM-based style transformation for speaker notes.
"""
import logging
import os
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger(__name__)


def _load_style_prompt(style_profile: str) -> str:
    """
    Load style prompt from markdown file.

    Args:
        style_profile: Style profile name (e.g., 'bruno')

    Returns:
        System prompt text

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompt_dir / f"{style_profile}_speaking_style.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Style prompt file not found: {prompt_file}")

    return prompt_file.read_text(encoding="utf-8")


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
        style_profile: Style profile name (e.g., 'bruno', 'generic', or any profile
                       with a corresponding <style_profile>_speaking_style.md file)

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

    # Load style prompt from file
    try:
        system_prompt = _load_style_prompt(style_profile)
    except FileNotFoundError:
        # Fallback to generic conversational style
        logger.warning(f"Style profile '{style_profile}' not found, using generic conversational style")
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
