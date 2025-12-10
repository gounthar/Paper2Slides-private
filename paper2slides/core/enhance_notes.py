"""
Speaker Notes Enhancement

Transforms structured speaker notes into narrative form using style-replicator agent.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def enhance_speaker_notes(checkpoint_path: str, style_profile: str = "bruno") -> int:
    """
    Enhance speaker notes in checkpoint_plan.json with narrative style.

    Args:
        checkpoint_path: Path to checkpoint_plan.json file
        style_profile: Style profile to use (default: bruno)

    Returns:
        Number of slides enhanced
    """
    from paper2slides.utils import load_json, save_json

    checkpoint_file = Path(checkpoint_path)
    if not checkpoint_file.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    # Load checkpoint
    logger.info("Loading checkpoint...")
    checkpoint_data = load_json(checkpoint_file)

    if not checkpoint_data or "plan" not in checkpoint_data:
        raise ValueError("Invalid checkpoint format: missing 'plan' key")

    plan = checkpoint_data["plan"]
    sections = plan.get("sections", [])

    if not sections:
        logger.warning("No sections found in checkpoint")
        return 0

    # Enhance each section's speaker notes
    enhanced_count = 0
    for idx, section in enumerate(sections, 1):
        slide_id = section.get("id", f"slide_{idx:02d}")
        title = section.get("title", "")
        content = section.get("content", "")
        speaker_notes = section.get("speaker_notes", {})

        # Skip if no structured speaker notes
        if not speaker_notes or not speaker_notes.get("talking_points"):
            logger.info(f"  [{idx}/{len(sections)}] {slide_id}: No structured notes, skipping")
            continue

        logger.info(f"  [{idx}/{len(sections)}] {slide_id}: Enhancing speaker notes...")

        try:
            # Transform structured notes to narrative
            narrative_notes = _transform_to_narrative(
                title=title,
                content=content,
                speaker_notes=speaker_notes,
                style_profile=style_profile
            )

            # Add enhanced narrative to section (keep structured notes for reference)
            section["speaker_notes_narrative"] = narrative_notes
            enhanced_count += 1

        except Exception as e:
            logger.error(f"  Failed to enhance {slide_id}: {e}")
            continue

    # Save enhanced checkpoint
    if enhanced_count > 0:
        logger.info(f"Saving enhanced checkpoint...")
        save_json(checkpoint_file, checkpoint_data)

    return enhanced_count


def _transform_to_narrative(
    title: str,
    content: str,
    speaker_notes: Dict[str, Any],
    style_profile: str
) -> str:
    """
    Transform structured speaker notes into narrative form.

    Uses the style-replicator agent (or custom logic) to generate
    a full narrative script from structured talking points.

    Args:
        title: Slide title
        content: Slide content
        speaker_notes: Structured speaker notes dict with talking_points, etc.
        style_profile: Style profile name

    Returns:
        Narrative speaker notes as a string
    """
    # Build structured input for transformation
    talking_points = speaker_notes.get("talking_points", [])
    key_terms = speaker_notes.get("key_terms", [])
    transition = speaker_notes.get("transition", "")
    duration = speaker_notes.get("duration_minutes", 2)

    # Create a prompt for the style-replicator agent
    structured_text = f"""# Speaker Notes for: {title}

## Talking Points:
{chr(10).join(f'- {point}' for point in talking_points)}

## Key Terms to Emphasize:
{', '.join(key_terms)}

## Transition:
{transition}

## Context (Slide Content):
{content[:500]}

## Duration: {duration} minutes

---

Transform these bullet-point talking points into a complete narrative script that a speaker can read aloud naturally. The script should:
- Be conversational and engaging
- Incorporate the key terms naturally
- Maintain the {duration}-minute duration
- End with the transition phrase
- Match the speaker's personal style (informal, direct, uses "here's the thing", parenthetical asides, etc.)
"""

    # Use Task tool to invoke style-replicator agent
    # For now, we'll use a subprocess-style invocation
    try:
        from paper2slides.core.agent_integration import invoke_style_replicator
        narrative = invoke_style_replicator(structured_text, style_profile)
        return narrative
    except Exception as e:
        logger.warning(f"Style transformation failed, using fallback: {e}")
        return _fallback_narrative(title, talking_points, key_terms, transition, duration)


def _fallback_narrative(
    title: str,
    talking_points: list,
    key_terms: list,
    transition: str,
    duration: int
) -> str:
    """
    Fallback: Create basic narrative without style transformation.
    """
    parts = [f"## {title}\n"]

    # Convert talking points to paragraphs
    for i, point in enumerate(talking_points, 1):
        parts.append(f"{point}.")
        if i < len(talking_points):
            parts.append("")  # Paragraph break

    # Add key terms
    if key_terms:
        parts.append(f"\n**Key terms to emphasize:** {', '.join(key_terms)}")

    # Add transition
    if transition:
        parts.append(f"\n**Transition to next slide:** {transition}")

    parts.append(f"\n*(Estimated time: {duration} minutes)*")

    return "\n".join(parts)
