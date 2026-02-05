import subprocess
import json
from pathlib import Path

# --- Config (tweak these) ---
VIDEO_PATH = "sample.mp4"
FPS = 1                 # sample 1 frame per second
BLOCK_SECONDS = 5    # one "temporal hash" block every 30 seconds
OUT_DIR = Path("blocks") # output folder
# ---------------------------

def run(cmd: list[str]) -> None:
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

def get_duration_seconds(video_path: str) -> float:
    # ffprobe returns duration in seconds (float)
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.check_output(cmd, text=True).strip()
    return float(result)

def extract_block(video_path: str, start: int, duration: int, out_dir: Path, fps: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Extract frames for this time window
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-t", str(duration),
        "-i", video_path,
        "-vf", f"fps={fps}",
        str(out_dir / "frame_%04d.jpg"),
    ]
    run(cmd)

def main():
    OUT_DIR.mkdir(exist_ok=True)

    dur = get_duration_seconds(VIDEO_PATH)
    print(f"Video duration: {dur:.2f}s")

    blocks = []
    block_idx = 0

    start = 0
    while start < dur:
        end = min(start + BLOCK_SECONDS, int(dur))
        block_len = end - start
        block_folder = OUT_DIR / f"block_{block_idx:04d}_{start:06d}s_{end:06d}s"

        print(f"\nExtracting block {block_idx}: {start}s to {end}s ({block_len}s) -> {block_folder}")
        extract_block(VIDEO_PATH, start, block_len, block_folder, FPS)

        blocks.append({
            "block_idx": block_idx,
            "start_s": start,
            "end_s": end,
            "frames_dir": str(block_folder)
        })

        block_idx += 1
        start += BLOCK_SECONDS

    # Save a manifest of blocks (useful later for web + verification)
    manifest_path = OUT_DIR / "blocks_manifest.json"
    manifest_path.write_text(json.dumps({
        "video_path": VIDEO_PATH,
        "fps": FPS,
        "block_seconds": BLOCK_SECONDS,
        "blocks": blocks
    }, indent=2))

    print(f"\nDone. Block manifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()
