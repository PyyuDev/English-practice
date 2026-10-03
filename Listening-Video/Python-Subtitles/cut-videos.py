import os
import subprocess
from pathlib import Path

# --- CONFIGURATION ---
INPUT_DIR = Path("./Videos")    # Folder containing your original videos
OUTPUT_DIR = Path("./videocutted")  # Folder where split segments will be saved
SEGMENT_LENGTH_SECONDS = 1800         # 30 minutes = 30 * 60 = 1800 seconds

# Supported video extensions
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"}

def split_video(input_file: Path, output_folder: Path):
    """Splits a single video into 30-minute chunks without re-encoding."""
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Pattern for output filenames (e.g., video_part001.mp4, video_part002.mp4)
    file_stem = input_file.stem
    file_ext = input_file.suffix
    output_pattern = output_folder / f"{file_stem}_part%03d{file_ext}"

    print(f"Processing: {input_file.name} ...")

    # FFmpeg command: splits by segment time and copies streams directly (no quality loss, very fast)
    command = [
        "ffmpeg",
        "-i", str(input_file),
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(SEGMENT_LENGTH_SECONDS),
        "-f", "segment",
        "-reset_timestamps", "1",
        str(output_pattern)
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✓ Finished splitting {input_file.name}\n")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error processing {input_file.name}: {e.stderr.decode()}\n")

def process_all_videos():
    """Finds all videos in INPUT_DIR and processes them."""
    if not INPUT_DIR.exists():
        print(f"Directory '{INPUT_DIR}' does not exist. Creating it now...")
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Please put your video files into '{INPUT_DIR.resolve()}' and re-run the script.")
        return

    video_files = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS]

    if not video_files:
        print(f"No video files found in '{INPUT_DIR.resolve()}'.")
        return

    print(f"Found {len(video_files)} video(s) to process.\n")

    for video_file in video_files:
        # Create a subfolder inside OUTPUT_DIR for each video's segments
        video_output_dir = OUTPUT_DIR / video_file.stem
        split_video(video_file, video_output_dir)

if __name__ == "__main__":
    process_all_videos()