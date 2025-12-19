Baseline Temporal Content Hashing Prototype

This repository implements a baseline temporal content hashing (TCH) pipeline for video integrity verification. The system is inspired by the ARCHANGEL approach to tamper-proofing video archives, but is deliberately simplified to establish correctness, reproducibility, and clear tamper localisation before introducing codec robustness or learned models.

The baseline pipeline supports:

Block-based temporal sampling of videos

Deterministic per-block fingerprint generation

Verification of candidate videos against a stored reference

Localisation of tampering to specific time intervals

At this stage, the system is not codec-robust by design and serves as a correctness benchmark for later enhancements.

Baseline Pipeline Overview

The baseline pipeline consists of three stages:

Block-based frame extraction

Per-block fingerprint computation

Verification and mismatch localisation

Each stage is implemented as a standalone script to support modular development and later integration into a web-based or asynchronous processing system.

1. Block-Based Frame Extraction

Script:

scripts/extract_blocks.py


This script:

Reads a video file (sample.mp4)

Determines its duration using ffprobe

Divides the video into fixed-length temporal blocks (default: 30 seconds)

Samples frames within each block at a fixed rate (default: 1 frame per second)

Writes extracted frames into per-block directories

Example output structure:

blocks/
  block_0000_000000s_000030s/
    frame_0001.jpg
    frame_0002.jpg
  block_0001_000030s_000060s/
    frame_0001.jpg
    frame_0002.jpg


A manifest file (blocks_manifest.json) is generated to record block boundaries, sampling parameters, and frame locations.

Run:
python scripts/extract_blocks.py

2. Baseline Per-Block Fingerprint Generation

Script:

scripts/block_hash_baseline.py


This script computes a deterministic fingerprint per temporal block:

Each sampled frame is hashed using SHA-256

Frame hashes within a block are concatenated in temporal order

The concatenated string is hashed again using SHA-256 to produce a single block hash

The resulting reference fingerprints are written to:

blocks/block_hashes_baseline.json


This file represents the reference temporal content hash sequence for the video.

Run:
python scripts/block_hash_baseline.py

3. Verification and Tamper Localisation

Script:

scripts/verify_blocks_baseline.py


This script verifies a candidate video against the stored reference by:

Repeating block-based frame extraction using identical parameters

Recomputing per-block fingerprints

Comparing candidate block hashes against reference hashes

Reporting mismatched blocks and their time ranges

Verification results include:

A binary verdict (PASS / FAIL)

A list of mismatched blocks with temporal localisation

A structured verification report is saved to:

verify_tmp/verify_result.json

Run:
python scripts/verify_blocks_baseline.py


Expected result when verifying the original video:

VERDICT: PASS (no mismatched blocks)