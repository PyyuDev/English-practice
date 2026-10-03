import json
import sys
from datetime import timedelta


def format_timestamp(seconds: float) -> str:
    """Converts seconds (e.g. 12.5) to SRT timestamp format (00:00:12,500)."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def json_to_srt(json_path: str, srt_path: str):
    # Read the JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        subtitles = json.load(f)

    # Write the SRT file
    with open(srt_path, "w", encoding="utf-8") as f:
        for index, item in enumerate(subtitles, start=1):
            start = format_timestamp(item.get("Start", item.get("start", 0)))
            end = format_timestamp(item.get("End", item.get("end", 0)))

            text_en = item.get("TextEn", item.get("textEn", ""))
            text_es = item.get("TextEs", item.get("textEs", ""))

            # Combine English and Spanish lines
            subtitle_text = text_en
            if text_es:
                subtitle_text += f"\n{text_es}"

            # Write SRT entry
            f.write(f"{index}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{subtitle_text}\n\n")

    print(
        f"Successfully converted '{json_path}' to '{srt_path}' with {len(subtitles)} entries!"
    )


if __name__ == "__main__":
    # Check if a filename was provided as an argument, otherwise use default names
    json_file = "./transcripciones_listas/neon_genesis_ep_3.json"
    srt_file = "./subtitlesxd.srt"

    json_to_srt(json_file, srt_file)