# Complete Workflow: PowerPoint with Narrative Speaker Notes

This guide shows you how to generate a PowerPoint presentation with **full narrative speaker notes** that you can read aloud during your presentation.

## What This Workflow Produces

Instead of basic bullet points, you get conversational scripts like:

> "Here's the thing about RISC-V64: the official GitHub Actions runner? It doesn't work. So we're using github-act-runner instead - it's a Go-based alternative that actually runs on RISC-V64..."

Perfect for:
- Practice sessions
- Reading aloud during live presentations
- Memorization aids
- Presenter training

## Prerequisites

### 1. OpenAI API Key

You need an OpenAI API key for GPT-4o to generate narrative notes.

**Get a key:**
1. Sign up at https://platform.openai.com/signup
2. Go to https://platform.openai.com/api-keys
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

**Add to your environment:**

Edit `paper2slides/.env` and add:
```bash
RAG_LLM_API_KEY=sk-your-actual-openai-key-here
```

**Cost estimate:** ~$0.05-0.20 per presentation (6 slides)

### 2. Image Generation Tool

You'll need one of these for generating slide images:
- **Gemini** (https://gemini.google.com) - Free, Google's AI
- **Nano Banana** (https://nanobanana.app) - Specialized for slides
- Any other image generator

## The Complete Workflow

### Step 1: Generate Slides with Structured Notes

This creates the slide outline, prompts for images, and structured speaker notes.

```bash
python -m paper2slides \
  --input /path/to/your-document.pdf \
  --content general \
  --output slides \
  --style academic \
  --length short \
  --export-prompts
```

**Parameters explained:**
- `--input`: Your source document (PDF, Word, Markdown, etc.)
- `--content general`: For general presentations (use `paper` for academic papers)
- `--output slides`: Generate slides (not poster)
- `--style academic`: Use academic style (or `doraemon`, or custom description)
- `--length short`: Short presentation (~6 slides; use `medium` or `long` for more)
- `--export-prompts`: Export prompts for manual image generation

**What gets created:**

```
outputs/your-document/general/normal/slides_academic_short/
├── checkpoint_plan.json          # Contains structured speaker notes
├── checkpoint_rag.json
├── checkpoint_summary.json
└── 20251210_123456/             # Timestamped run
    └── prompts/
        ├── INSTRUCTIONS.md      # How to use Nano Banana
        ├── slide_01_prompt.txt  # Text prompt for slide 1
        ├── slide_01_images/     # Directory for slide 1 image
        ├── slide_02_prompt.txt
        ├── slide_02_images/
        └── ...
```

**Time:** 2-5 minutes

### Step 2: Enhance Speaker Notes to Narrative Style

Transform the structured bullet points into flowing narrative scripts.

```bash
python -m paper2slides --enhance-speaker-notes \
  outputs/your-document/general/normal/slides_academic_short/checkpoint_plan.json \
  --speaker-style bruno
```

**What happens:**
- Reads structured notes (talking points, key terms, transitions)
- Calls GPT-4o to transform into conversational narrative
- Saves enhanced notes as `speaker_notes_narrative` in checkpoint
- Original structured notes are preserved

**Output example:**

Before (structured):
```
• Explain the importance of github-act-runner for RISC-V64
• Discuss hardware recommendations
• Walkthrough setup process

Key terms: github-act-runner, BananaPi F3, systemd
```

After (narrative):
```
Here's the thing about RISC-V64: the official GitHub Actions runner?
It doesn't work. So we're using github-act-runner instead - it's a
Go-based alternative that actually runs on RISC-V64.

Now, hardware. You *can* run this on 4 cores and 4GB RAM, but honestly?
You'll be waiting a lot. The sweet spot is the BananaPi F3 - 8 cores,
16GB RAM, running Armbian Trixie. Trust me, the extra headroom makes
a huge difference when you're compiling Go binaries...
```

**Time:** ~30 seconds (5-10 seconds per slide)

### Step 3: Generate Images

Use the exported prompts to generate slide images manually.

**Option A: Gemini (Recommended for beginners)**

1. Go to https://gemini.google.com
2. Open `slide_01_prompt.txt`
3. Copy the entire prompt
4. Paste into Gemini chat
5. Download the generated image
6. Save as `generated.png` in `slide_01_images/` directory
7. Repeat for all slides

**Option B: Nano Banana (Better for slides)**

1. Go to https://nanobanana.app
2. Follow `INSTRUCTIONS.md` in the prompts directory
3. Generate all slides
4. Download images
5. Rename to `generated.png` and place in correct `slide_XX_images/` directories

**Expected file structure after this step:**

```
outputs/.../20251210_123456/prompts/
├── slide_01_images/
│   └── generated.png          # ← Your generated image
├── slide_02_images/
│   └── generated.png          # ← Your generated image
└── ...
```

**Time:** 5-15 minutes (depending on tool and number of slides)

### Step 4: Create PowerPoint with Narrative Notes

Import the generated images and create the final PPTX with narrative notes.

```bash
python -m paper2slides --import-images \
  outputs/your-document/general/normal/slides_academic_short/20251210_123456/prompts
```

**What happens:**
- Scans `prompts/` directory for `slide_XX_images/generated.png` files
- Creates a PowerPoint presentation (16:9 format)
- Adds images as full-slide backgrounds
- Loads narrative speaker notes from checkpoint
- Embeds notes in PowerPoint's notes section

**Output:**
```
outputs/.../20251210_123456/slides.pptx
```

**Open it:**
```bash
# macOS
open outputs/.../20251210_123456/slides.pptx

# Linux
xdg-open outputs/.../20251210_123456/slides.pptx

# Windows
start outputs/.../20251210_123456/slides.pptx
```

**Time:** ~5 seconds

## Quick Reference: All Commands in One Place

```bash
# Set up project name variable for convenience
export PROJECT="your-document-name"
export BASE="outputs/${PROJECT}/general/normal/slides_academic_short"

# Step 1: Generate slides with structured notes
python -m paper2slides \
  --input /path/to/${PROJECT}.pdf \
  --content general \
  --output slides \
  --style academic \
  --length short \
  --export-prompts

# Step 2: Enhance to narrative style
python -m paper2slides \
  --enhance-speaker-notes ${BASE}/checkpoint_plan.json \
  --speaker-style bruno

# Step 3: Generate images manually (use Gemini/Nano Banana)
# Save as: ${BASE}/YYYYMMDD_HHMMSS/prompts/slide_XX_images/generated.png

# Step 4: Create PowerPoint
export PROMPTS=$(ls -td ${BASE}/*/prompts | head -1)
python -m paper2slides --import-images ${PROMPTS}

# Step 5: Open the result
open ${PROMPTS}/../slides.pptx  # macOS
```

## Real Example: RISC-V Docker Story

Here's a concrete example with actual paths:

```bash
# Step 1: Generate
python -m paper2slides \
  --input /tmp/riscv-docker-story \
  --content general \
  --output slides \
  --style academic \
  --length short \
  --export-prompts

# Output: outputs/riscv-docker-story/general/normal/slides_academic_short/checkpoint_plan.json
# Output: outputs/riscv-docker-story/general/normal/slides_academic_short/20251210_102306/prompts/

# Step 2: Enhance
python -m paper2slides --enhance-speaker-notes \
  outputs/riscv-docker-story/general/normal/slides_academic_short/checkpoint_plan.json \
  --speaker-style bruno

# Step 3: Generated images manually, saved to:
# outputs/.../20251210_102306/prompts/slide_01_images/generated.png
# outputs/.../20251210_102306/prompts/slide_02_images/generated.png
# ... etc

# Step 4: Create PPTX
python -m paper2slides --import-images \
  outputs/riscv-docker-story/general/normal/slides_academic_short/20251210_102306/prompts

# Output: outputs/.../20251210_102306/slides.pptx
```

## Viewing Your Narrative Notes

### In PowerPoint
1. Open the PPTX file
2. Go to View → Notes Page (or View → Normal, bottom pane)
3. See full narrative scripts below each slide

### From Command Line

View slide 2's narrative:
```bash
jq -r '.plan.sections[1].speaker_notes_narrative' \
  outputs/your-document/general/normal/slides_academic_short/checkpoint_plan.json
```

View all narratives:
```bash
jq -r '.plan.sections[] | "\n## \(.title)\n\n\(.speaker_notes_narrative)"' \
  outputs/your-document/general/normal/slides_academic_short/checkpoint_plan.json
```

## Troubleshooting

### "RAG_LLM_API_KEY environment variable is not set"

**Problem:** The OpenAI API key isn't loaded.

**Solution:**
1. Check that `paper2slides/.env` exists and contains your key:
   ```bash
   cat paper2slides/.env | grep RAG_LLM_API_KEY
   ```
2. Verify the key starts with `sk-`
3. Restart your terminal session if you just added it

**Alternative:** Set it inline:
```bash
export RAG_LLM_API_KEY="sk-your-key"
python -m paper2slides --enhance-speaker-notes ...
```

### "No structured notes, skipping"

**Problem:** Some slides don't have structured notes.

**This is normal!** Title slides and conclusion slides often don't have talking points.

**Solution:** No action needed. Only slides with talking points get narrative enhancement.

### "Missing slides" warning during import

**Problem:** Some `slide_XX_images/generated.png` files are missing.

**Solution:**
1. Check which slides are missing:
   ```bash
   ls outputs/.../prompts/slide_*/generated.png
   ```
2. Generate the missing images
3. Save them as `generated.png` in the correct directories
4. Re-run the import command

### Generated narrative is too formal/different style

**Problem:** The narrative doesn't match your speaking style.

**Current limitation:** Only `bruno` style is implemented (conversational, direct, with humor).

**Workaround:** Edit the checkpoint manually:
```bash
jq '.plan.sections[1].speaker_notes_narrative = "Your custom narrative here"' \
  checkpoint_plan.json > checkpoint_plan_edited.json
mv checkpoint_plan_edited.json checkpoint_plan.json
```

**Future:** More style profiles coming soon.

### Import fails with "checkpoint not found"

**Problem:** Import can't find the checkpoint file.

**Solution:** The checkpoint is always 2 levels up from `prompts/`:
```bash
# If prompts are at: outputs/.../20251210_102306/prompts/
# Checkpoint is at:   outputs/.../checkpoint_plan.json

# Verify checkpoint exists
ls outputs/your-document/general/normal/slides_academic_short/checkpoint_plan.json
```

## Tips and Best Practices

### 1. Use Meaningful Project Names

Instead of `paper.pdf`, use descriptive names:
```bash
--input /tmp/riscv-docker-setup-guide
```

This makes outputs easier to find:
```
outputs/riscv-docker-setup-guide/...  # ✅ Clear
outputs/paper/...                      # ❌ Confusing
```

### 2. Keep API Costs Low

Each narrative enhancement costs ~$0.01-0.03 per slide. To minimize costs:

- ✅ Generate once, import multiple times (enhancement saves to checkpoint)
- ✅ Use fallback mode (free) for drafts: just skip step 2
- ❌ Don't repeatedly enhance the same checkpoint

### 3. Version Your Checkpoints

Before enhancing, make a backup:
```bash
cp checkpoint_plan.json checkpoint_plan_original.json
```

This lets you:
- Compare structured vs narrative notes
- Try different enhancement approaches
- Roll back if needed

### 4. Iterate on Images

You can regenerate images without re-running the whole pipeline:

1. Generate new images
2. Replace `generated.png` files
3. Re-run import: `python -m paper2slides --import-images prompts/`

The narrative notes stay the same!

### 5. Script Your Workflow

Create a shell script for your project:

```bash
#!/bin/bash
# generate-presentation.sh

PROJECT="my-talk"
INPUT="/path/to/source.pdf"
BASE="outputs/${PROJECT}/general/normal/slides_academic_short"

# Generate
python -m paper2slides \
  --input "${INPUT}" \
  --content general \
  --output slides \
  --export-prompts

# Enhance
python -m paper2slides \
  --enhance-speaker-notes ${BASE}/checkpoint_plan.json \
  --speaker-style bruno

echo "✅ Ready for manual image generation!"
echo "📁 Prompts directory: ${BASE}/$(ls -t ${BASE} | head -1)/prompts/"
```

## What's Next?

After generating your PPTX:

1. **Practice with notes:** Open in PowerPoint, View → Presenter mode
2. **Refine narratives:** Edit notes directly in PowerPoint's notes section
3. **Print notes:** File → Print → Print Layout → Notes Pages
4. **Share with team:** Send PPTX with notes for others to present

## Advanced: Customizing the Style

Want to create your own speaking style? Edit `paper2slides/core/agent_integration.py`:

```python
if style_profile == "your-style":
    system_prompt = """Transform speaker notes into [your style description].

    Style guidelines:
    - [Your characteristic 1]
    - [Your characteristic 2]
    - etc.
    """
```

Then use:
```bash
python -m paper2slides --enhance-speaker-notes checkpoint.json --speaker-style your-style
```

## Support

Issues? Questions?
- GitHub Issues: https://github.com/gounthar/Paper2Slides-private/issues
- Check existing workflows in `outputs/` for examples

---

**Last Updated:** 2025-12-10
**Version:** 1.0
