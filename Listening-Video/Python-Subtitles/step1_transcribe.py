import json
import os
from pathlib import Path
from rich.console import Console
import whisper

console = Console()

def split_segment_by_interval(start, end, text, interval=15.0):
    """Splits a single segment into sub-segments bounded by 'interval' seconds."""
    sub_segments = []
    current_start = start

    while current_start < end:
        next_boundary = ((current_start // interval) + 1) * interval
        current_end = min(end, next_boundary)

        total_duration = end - start
        if total_duration > 0:
            start_ratio = (current_start - start) / total_duration
            end_ratio = (current_end - start) / total_duration

            char_start = int(start_ratio * len(text))
            char_end = int(end_ratio * len(text))
            sub_text = text[char_start:char_end].strip()
        else:
            sub_text = text.strip()

        if sub_text:
            sub_segments.append({
                "start": round(current_start, 2),
                "end": round(current_end, 2),
                "textEn": sub_text
            })

        current_start = current_end

    return sub_segments


def transcribe_video(video_path: str, output_folder: str, model, device: str, interval: float = 15.0) -> str:
    """Transcribes a single video and outputs English JSON segments."""
    video_path_obj = Path(video_path)
    nombre_base = video_path_obj.stem
    os.makedirs(output_folder, exist_ok=True)
    ruta_json_salida = os.path.join(output_folder, f"{nombre_base}.json")

    console.print(f"\n[bold yellow]--- Transcribing: {nombre_base} ---[/]")

    result = model.transcribe(
        str(video_path_obj), language="en", fp16=(device == "cuda")
    )

    data_karaoke = []
    for s in result["segments"]:
        start = round(s["start"], 2)
        end = round(s["end"], 2)
        text = s["text"].strip()

        chunks = split_segment_by_interval(start, end, text, interval=interval)
        for chunk in chunks:
            data_karaoke.append(chunk)

    with open(ruta_json_salida, "w", encoding="utf-8") as f:
        json.dump(data_karaoke, f, indent=4, ensure_ascii=False)

    console.print(f"[bold green]✓ Transcription saved:[/] [cyan]{ruta_json_salida}[/]")
    return ruta_json_salida