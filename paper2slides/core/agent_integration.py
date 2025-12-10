"""
Agent Integration for Paper2Slides

Provides integration with Claude Code agents (style-replicator, etc.)
"""
import logging
import subprocess
import json
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def invoke_style_replicator(text: str, style_profile: str = "bruno") -> str:
    """
    Invoke the style-replicator agent to transform text into narrative style.

    This uses the Claude Code CLI to invoke the style-replicator agent.
    Since we can't directly use the Task tool from Python, we use subprocess.

    Args:
        text: Structured text to transform
        style_profile: Style profile (currently only 'bruno' is supported)

    Returns:
        Transformed narrative text

    Raises:
        Exception: If agent invocation fails
    """
    # Create temp file with input text
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        input_file = f.name

    output_file = input_file.replace('.txt', '_output.txt')

    try:
        # Note: This is a placeholder for the actual integration
        # In reality, we can't easily invoke Claude Code agents from subprocess
        # because they're part of the same Claude Code session.
        #
        # Better approach: Use the @agent syntax or Task tool if available,
        # or implement the style transformation directly using an LLM API call.

        logger.warning("Style-replicator agent integration not yet implemented")
        logger.info("Using direct LLM transformation instead...")

        # Use OpenAI API directly (simpler than subprocess)
        return _transform_via_llm(text, style_profile)

    finally:
        # Cleanup temp files
        try:
            Path(input_file).unlink()
            if Path(output_file).exists():
                Path(output_file).unlink()
        except:
            pass


def _transform_via_llm(structured_text: str, style_profile: str) -> str:
    """
    Transform structured notes using LLM API directly.

    This is more practical than trying to invoke agents via subprocess.
    """
    import os
    from openai import OpenAI

    api_key = os.getenv("RAG_LLM_API_KEY", "")
    base_url = os.getenv("RAG_LLM_BASE_URL")

    if not api_key:
        raise ValueError("RAG_LLM_API_KEY not set")

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
        logger.error(f"LLM transformation failed: {e}")
        raise
