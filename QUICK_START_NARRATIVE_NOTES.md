# Quick Start: PowerPoint with Narrative Speaker Notes

## The 4-Step Process

```bash
# 1. Generate slides with structured notes
python -m paper2slides --input paper.pdf --content general --output slides --export-prompts

# 2. Enhance to narrative style
python -m paper2slides --enhance-speaker-notes \
  outputs/your-paper/general/normal/slides_academic_short/checkpoint_plan.json \
  --speaker-style bruno

# 3. Generate images manually (Gemini/Nano Banana)
# Save as: outputs/.../YYYYMMDD_HHMMSS/prompts/slide_XX_images/generated.png

# 4. Create PowerPoint
python -m paper2slides --import-images \
  outputs/your-paper/general/normal/slides_academic_short/YYYYMMDD_HHMMSS/prompts
```

## Prerequisites

Add to `paper2slides/.env`:
```bash
RAG_LLM_API_KEY=sk-your-openai-api-key-here
```

Get key at: https://platform.openai.com/api-keys

## Output

PPTX file at: `outputs/.../YYYYMMDD_HHMMSS/slides.pptx`

With narrative notes like:
> "Here's the thing about RISC-V64: the official GitHub Actions runner? It doesn't work. So we're using github-act-runner instead..."

## Full Documentation

📖 **[Complete Guide](docs/NARRATIVE_SPEAKER_NOTES_WORKFLOW.md)** - Detailed workflow with examples and troubleshooting

## Common Commands

```bash
# View narrative for slide 2
jq -r '.plan.sections[1].speaker_notes_narrative' checkpoint_plan.json

# Find latest prompts directory
ls -td outputs/*/general/normal/slides_academic_short/*/prompts | head -1

# Open result
open outputs/.../slides.pptx      # macOS
xdg-open outputs/.../slides.pptx  # Linux
```

## Cost

~$0.05-0.20 per presentation (6 slides)
