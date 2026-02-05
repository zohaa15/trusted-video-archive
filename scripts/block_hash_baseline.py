import json
import hashlib
from pathlib import Path

MANIFEST = Path("blocks/blocks_manifest.json")
OUT = Path("blocks/block_hashes_baseline.json")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    data = json.loads(MANIFEST.read_text())
    blocks = data["blocks"]

    results = []
    for b in blocks:
        frames_dir = Path(b["frames_dir"])
        frame_files = sorted(frames_dir.glob("frame_*.jpg"))

        # Baseline block hash: hash of concatenated frame hashes
        frame_hashes = [sha256_file(p) for p in frame_files]
        combined = ("".join(frame_hashes)).encode("utf-8")
        block_hash = hashlib.sha256(combined).hexdigest()

        results.append({
            "block_idx": b["block_idx"],
            "start_s": b["start_s"],
            "end_s": b["end_s"],
            "num_frames": len(frame_files),
            "block_hash": block_hash
        })
        print(f"Block {b['block_idx']} [{b['start_s']}–{b['end_s']}s]: {block_hash[:12]}...")

    OUT.write_text(json.dumps({
        "video_path": data["video_path"],
        "fps": data["fps"],
        "block_seconds": data["block_seconds"],
        "block_hashes": results
    }, indent=2))

    print(f"\nSaved baseline block hashes to: {OUT}")

if __name__ == "__main__":
    main()
