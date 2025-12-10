"""
Paper2Slides - Main Entry Point
"""

import os
import logging
import argparse
import asyncio
from pathlib import Path

from paper2slides.utils import setup_logging
from paper2slides.utils.path_utils import (
    normalize_input_path,
    get_project_name,
    parse_style,
)
from paper2slides.core import (
    get_base_dir,
    get_config_dir,
    detect_start_stage,
    run_pipeline,
    list_outputs,
    STAGES,
)

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")

# Get project root directory (parent of paper2slides package)
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT_DIR = str(PROJECT_ROOT / "outputs")

logger = logging.getLogger(__name__)


def main():
    """Main entry point for Paper2Slides CLI."""
    parser = argparse.ArgumentParser(
        description="Paper2Slides - Auto-reuses checkpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--input", "-i", help="Input file or directory path (relative or absolute)")
    parser.add_argument("--content", choices=["paper", "general"], default="paper",
                        help="Content type (default: paper)")
    parser.add_argument("--output", choices=["poster", "slides"], default="poster",
                        help="Output type (default: poster)")
    parser.add_argument("--style", default="doraemon",
                        help="Style: academic, doraemon, or custom description")
    parser.add_argument("--length", choices=["short", "medium", "long"], default="short",
                        help="Slides length (default: short)")
    parser.add_argument("--density", choices=["sparse", "medium", "dense"], default="medium",
                        help="Poster density (default: medium)")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--from-stage", choices=STAGES,
                        help="Force re-run from specific stage")
    parser.add_argument("--list", action="store_true",
                        help="List all outputs")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--fast", action="store_true",
                        help="Fast mode: parse only, no RAG indexing (direct LLM query)")
    parser.add_argument("--parallel", type=int, nargs='?', const=2, default=None,
                        help="Enable parallel slide generation with N workers (default: 2 if specified)")
    parser.add_argument("--export-prompts", action="store_true",
                        help="Export Nano Banana prompts instead of calling image generation API")
    parser.add_argument("--import-images", type=str, metavar="DIR",
                        help="Import manually generated images from prompt directory to create PPTX")
    parser.add_argument("--enhance-speaker-notes", type=str, metavar="CHECKPOINT",
                        help="Enhance speaker notes in checkpoint_plan.json with narrative style (e.g., outputs/.../checkpoint_plan.json)")
    parser.add_argument("--speaker-style", type=str, default="bruno",
                        help="Speaker notes style profile (default: bruno)")
    parser.add_argument("--pptx", action="store_true",
                        help="Generate PPTX output instead of PDF (default for prompt export mode)")

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=logging.DEBUG if args.debug else logging.INFO)
    
    if args.list:
        list_outputs(args.output_dir)
        return

    # Handle --enhance-speaker-notes mode (standalone operation)
    if args.enhance_speaker_notes:
        from paper2slides.core.enhance_notes import enhance_speaker_notes
        checkpoint_path = Path(args.enhance_speaker_notes)
        if not checkpoint_path.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_path}")
            return
        if not checkpoint_path.is_file():
            logger.error(f"Checkpoint path is not a file: {checkpoint_path}")
            return

        logger.info(f"Enhancing speaker notes in: {checkpoint_path}")
        logger.info(f"Using style profile: {args.speaker_style}")
        try:
            enhanced_count = enhance_speaker_notes(str(checkpoint_path), args.speaker_style)
            logger.info(f"Successfully enhanced {enhanced_count} slides with narrative speaker notes")
            logger.info(f"Updated checkpoint: {checkpoint_path}")
        except Exception:
            logger.exception("Enhancement failed")
        return

    # Handle --import-images mode (standalone operation)
    if args.import_images:
        from paper2slides.generator.image_generator import import_generated_images
        import_dir = Path(args.import_images)
        if not import_dir.exists():
            logger.error(f"Import directory not found: {import_dir}")
            return
        if not import_dir.is_dir():
            logger.error(f"Import path is not a directory: {import_dir}")
            return

        # Determine output path
        output_pptx = import_dir.parent / "slides.pptx"
        logger.info(f"Importing images from: {import_dir}")
        try:
            missing = import_generated_images(str(import_dir), str(output_pptx))
            if missing:
                logger.warning(f"Missing slides: {missing}")
                logger.info("Generate the missing images and re-run import")
            else:
                logger.info(f"Successfully created: {output_pptx}")
        except ValueError as e:
            logger.error(f"Import failed: {e}")
            logger.info("Ensure the directory contains slide_XX_images/ subdirectories with generated.png files")
        return

    if not args.input:
        parser.print_help()
        return
    
    # Normalize input path (convert to absolute path)
    try:
        input_path = normalize_input_path(args.input)
        path = Path(input_path)
        if path.is_file():
            logger.info(f"Input: {path.name} (file)")
        else:
            logger.info(f"Input: {path.name} (directory)")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return
    
    # Build config
    style_type, custom_style = parse_style(args.style)

    # Prompt-export workflow is slides-only; override output type in that case
    output_type = "slides" if args.export_prompts else args.output

    config = {
        "input_path": input_path,
        "content_type": args.content,
        "output_type": output_type,
        "style": style_type,
        "custom_style": custom_style,
        "slides_length": args.length,
        "poster_density": args.density,
        "fast_mode": args.fast,
        "max_workers": args.parallel if args.parallel else 1,
        "export_prompts": args.export_prompts,
        "use_pptx": args.pptx or args.export_prompts,  # Default to PPTX in prompt export mode
    }
    
    # Determine paths
    project_name = get_project_name(args.input)
    base_dir = get_base_dir(args.output_dir, project_name, args.content)
    config_dir = get_config_dir(base_dir, config)
    
    logger.info("")
    logger.info(f"Project: {project_name}")
    logger.info(f"Base: {base_dir}")
    logger.info(f"Config: {config_dir.name}")
    
    # Determine start stage
    if args.from_stage:
        from_stage = args.from_stage
    else:
        from_stage = detect_start_stage(base_dir, config_dir, config)
    
    if from_stage != "rag":
        logger.info(f"Reusing existing checkpoints, starting from: {from_stage}")
    
    # Run pipeline (CLI mode: no session_id or session_manager for cancellation)
    asyncio.run(run_pipeline(base_dir, config_dir, config, from_stage))


if __name__ == "__main__":
    main()
