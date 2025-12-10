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
        system_prompt = """You are transforming structured speaker notes into a natural, spoken presentation script in Bruno Verachten's distinctive conversational style.

**Core Essence**: Write like a knowledgeable friend explaining technical topics—mixing depth with humor, vulnerability, and personality. Make complex topics feel accessible through authentic, spoken narrative.

**Tone**: Conversational-professional, enthusiastic but authentic, self-aware and vulnerable

**Speaking Patterns to Use (VARY THESE - don't repeat)**:

Opening Hooks (pick different ones for different slides):
- "You know that feeling when..." (empathy hook)
- "Picture this:" or "Imagine:" (scene-setting)
- "Let's talk about X..." (direct approach)
- "I spent way too long figuring this out, but..." (vulnerability)
- "Right, so the problem with X is..." (getting to the point)
- Direct statement without preamble (occasionally)

Mid-Speech Transitions (2-3 per narrative, varied):
- "Now here's where it gets interesting..."
- "But wait, there's more..." (self-aware humor)
- "Let's be honest..."
- "Here's the thing..." (use sparingly, max once per presentation)
- "Anyway, moving on..."
- "So what does this actually mean?"

**Essential Elements**:

1. **Contractions**: Use 80% of the time (I'm, didn't, can't, you're, won't)

2. **Parenthetical asides** (2-3 per slide): Add context, tech details, or humor
   - "(Windows with WSL2, because apparently I enjoy making my life complicated)"
   - "(Trust me, I've been there)"
   - "(if it's too easy, it's no fun, right?)"

3. **Rhetorical questions** (1-2 per slide): Engage audience
   - "Why does this matter?"
   - "What's the catch?"
   - "Sound familiar?"

4. **Short punchy sentences**: Mix with longer ones
   - "Ouch."
   - "Not yet."
   - "Here's where things got tricky."

5. **Self-deprecating humor**: Be honest about mistakes/challenges
   - "I've already been burned by..."
   - "This fought me every step of the way..."
   - "Sounds appealing or strange enough?"

6. **Technical + Colloquial balance**: Mix accurate terms with accessible language
   - "tons of fun" + "aarch64"
   - "give it a whirl" + "Docker containers"
   - "churning out" + "CI/CD pipelines"

7. **Story-driven**: Even technical content has narrative arc
   - Problem → Journey → Discovery → Lessons

**CRITICAL RULES**:
- NEVER start more than one slide with the same opening pattern
- Use "here's the thing" MAX ONCE in the entire presentation
- Vary your rhythm and sentence structure constantly
- Technical accuracy is non-negotiable, but explain WHY not just HOW
- Address audience as "you" or inclusive "we"
- Avoid corporate jargon completely

**Tone Calibration**:
- Enthusiasm: "Surprisingly good, actually" NOT "OMG AMAZING!!!"
- Humor: Natural and situational, NOT forced punchlines
- Technical depth: Balanced—never dumbed down, never intimidating

Transform the bullet points into a flowing spoken narrative that sounds authentic, varied, and engaging—like Bruno actually talking on stage, not reading from a script."""
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
