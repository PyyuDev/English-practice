import os
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
import torch
import whisper
from transformers import MarianMTModel, MarianTokenizer

from step1_transcribe import transcribe_video
from step2_translate import translate_json

# --- CONFIGURATION ---
INPUT_VIDEOS_FOLDER = "./videocutted"
FOLDER_ENGLISH_JSON = "./mis_transcripciones"
FOLDER_SPANISH_JSON = "./transcripciones_listas"

WHISPER_MODEL_NAME = "small.en"
TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"
VALID_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

console = Console()

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    target_folder = Path(INPUT_VIDEOS_FOLDER)

    if not target_folder.exists() or not target_folder.is_dir():
        console.print(f"[bold red]Input video folder not found:[/] {INPUT_VIDEOS_FOLDER}")
        return

    # Find all videos
    video_files = [f for f in target_folder.iterdir() if f.suffix.lower() in VALID_EXTENSIONS]

    if not video_files:
        console.print(f"[bold red]No video files found in:[/] {INPUT_VIDEOS_FOLDER}")
        return

    console.print(f"[bold green]Found {len(video_files)} video(s) to process.[/]")

    # --- LOAD MODELS ONCE ---
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Load Whisper
        progress.add_task(
            f"Loading Whisper '[bold cyan]{WHISPER_MODEL_NAME}[/]' on [bold green]{device.upper()}[/]...",
            total=None,
        )
        whisper_model = whisper.load_model(WHISPER_MODEL_NAME).to(device)

        # Load MarianMT
        progress.add_task(
            f"Loading MarianMT '[bold cyan]{TRANSLATION_MODEL_NAME}[/]' on [bold green]{device.upper()}[/]...",
            total=None,
        )
        marian_tokenizer = MarianTokenizer.from_pretrained(TRANSLATION_MODEL_NAME)
        marian_model = MarianMTModel.from_pretrained(TRANSLATION_MODEL_NAME).to(device)

    # --- ITERATE THROUGH VIDEOS ---
    total_start_time = time.time()

    for idx, video_file in enumerate(video_files, start=1):
        console.print(f"\n[bold underline cyan]Processing File ({idx}/{len(video_files)}): {video_file.name}[/]")
        start_time = time.time()

        try:
            # 1. Transcribe
            json_en = transcribe_video(
                video_path=str(video_file),
                output_folder=FOLDER_ENGLISH_JSON,
                model=whisper_model,
                device=device,
                interval=15.0
            )

            # 2. Translate
            translate_json(
                json_path=json_en,
                output_folder=FOLDER_SPANISH_JSON,
                tokenizer=marian_tokenizer,
                model=marian_model,
                device=device
            )

            elapsed = round(time.time() - start_time, 2)
            console.print(f"[bold green]Finished {video_file.name} in {elapsed}s[/]")

        except Exception as e:
            console.print(f"[bold red]Failed processing {video_file.name}: {e}[/]")

    total_elapsed = round(time.time() - total_start_time, 2)
    console.print(f"\n[bold green] All {len(video_files)} video(s) processed in {total_elapsed}s![/]")

if __name__ == "__main__":
    main()