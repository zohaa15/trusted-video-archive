import json
import subprocess
import shutil
from pathlib import Path

# Reference hashes produced from the original
REFERENCE_HASHES = Path("blocks/block_hashes_baseline.json")

# Candidate video to verify (swap this path to a tampered/transcoded file later)
CANDIDATE_VIDEO = "sample.mp4"

# Sampling settings must match reference
FPS = 1
BLOCK_SECONDS = 5

TMP_DIR = Path("verify_tmp")

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)

def get_duration_seconds(video_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    return float(subprocess.check_output(cmd, text=True).strip())

def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def compute_candidate_block_hashes(video_path: str):
    dur = get_duration_seconds(video_path)
    TMP_DIR.mkdir(exist_ok=True)

    block_hashes = []
    block_idx = 0
    start = 0
    while start < dur:
        end = min(start + BLOCK_SECONDS, int(dur))
        block_len = end - start
        block_folder = TMP_DIR / f"block_{block_idx:04d}_{start:06d}s_{end:06d}s"
        if block_folder.exists():
            shutil.rmtree(block_folder)
        block_folder.mkdir(parents=True, exist_ok=True)

        # extract frames for this block
        run([
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(block_len),
            "-i", video_path,
            "-vf", f"fps={FPS}",
            str(block_folder / "frame_%04d.jpg"),
        ])

        frame_files = sorted(block_folder.glob("frame_*.jpg"))
        frame_hashes = [sha256_file(p) for p in frame_files]
        import hashlib
        combined = ("".join(frame_hashes)).encode("utf-8")
        block_hash = hashlib.sha256(combined).hexdigest()

        block_hashes.append({
            "block_idx": block_idx,
            "start_s": start,
            "end_s": end,
            "block_hash": block_hash
        })

        block_idx += 1
        start += BLOCK_SECONDS

    return block_hashes

def main():
    ref = json.loads(REFERENCE_HASHES.read_text())
    ref_blocks = {b["block_idx"]: b for b in ref["block_hashes"]}

    cand_blocks = compute_candidate_block_hashes(CANDIDATE_VIDEO)

    mismatches = []
    for b in cand_blocks:
        idx = b["block_idx"]
        if idx not in ref_blocks:
            mismatches.append({**b, "reason": "missing_reference"})
            continue

        if b["block_hash"] != ref_blocks[idx]["block_hash"]:
            mismatches.append({
                "block_idx": idx,
                "start_s": b["start_s"],
                "end_s": b["end_s"],
                "reason": "hash_mismatch"
            })

    if not mismatches:
        print("\nVERDICT: PASS (no mismatched blocks)")
    else:
        print("\nVERDICT: FAIL (mismatched blocks found)")
        for m in mismatches:
            print(f"- Block {m['block_idx']} [{m['start_s']}–{m['end_s']}s]: {m['reason']}")

    # Save results
    out = TMP_DIR / "verify_result.json"
    out.write_text(json.dumps({
        "candidate_video": CANDIDATE_VIDEO,
        "verdict": "PASS" if not mismatches else "FAIL",
        "mismatches": mismatches
    }, indent=2))
    print(f"\nSaved verify report: {out}")

if __name__ == "__main__":
    main()

