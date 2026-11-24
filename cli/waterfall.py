"""Terminal waterfall display and simple covert-channel detector.

Reads a WAV file, builds a spectrogram, prints a colour waterfall (time goes
down, frequency goes across), then reports the peak frequency and the
ON/OFF segments found in that band.

Usage:
    python waterfall.py ../data/samples/sim_sos.wav
    python waterfall.py recording.wav --fmin 100 --fmax 3000 --live
"""
import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dsp"))
from spectrogram import (band_energy, compute_spectrogram, detect_segments,
                         find_peak_frequency, load_wav)

PALETTE = [17, 18, 19, 20, 21, 27, 33, 39, 45, 51, 50, 49, 48, 47, 46,
           82, 118, 154, 190, 226, 220, 214, 208, 202, 196]


def cell(v):
    idx = int(np.clip(v, 0, 1) * (len(PALETTE) - 1))
    return f"\033[38;5;{PALETTE[idx]}m\u2588\033[0m"


def build_rows(S, freqs, fmin, fmax, width, group):
    """Reduce spectrogram to rows of `width` columns, normalised to 0..1."""
    mask = (freqs >= fmin) & (freqs <= fmax)
    sub = S[:, mask]
    n_rows = max(1, sub.shape[0] // group)
    sub = sub[:n_rows * group].reshape(n_rows, group, -1).mean(axis=1)
    cols = np.array_split(np.arange(sub.shape[1]), width)
    out = np.stack([sub[:, c].mean(axis=1) for c in cols if len(c)], axis=1)
    lo, hi = np.percentile(out, 5), np.percentile(out, 99.5)
    return np.clip((out - lo) / (hi - lo + 1e-9), 0, 1)


def main():
    ap = argparse.ArgumentParser(description="Terminal waterfall + detector")
    ap.add_argument("wav")
    ap.add_argument("--fmin", type=float, default=50)
    ap.add_argument("--fmax", type=float, default=3000)
    ap.add_argument("--width", type=int, default=80)
    ap.add_argument("--rows-per-sec", type=int, default=10)
    ap.add_argument("--live", action="store_true", help="replay in real time")
    args = ap.parse_args()

    os.system("")  # enables ANSI colours in Windows terminals
    x, rate = load_wav(args.wav)
    freqs, times, S = compute_spectrogram(x, rate)
    hop_s = times[1] - times[0]
    group = max(1, int(round(1.0 / (args.rows_per_sec * hop_s))))
    rows = build_rows(S, freqs, args.fmin, args.fmax, args.width, group)

    print(f"{args.wav}: {len(x) / rate:.1f}s at {rate} Hz")
    print(f"Waterfall {args.fmin:.0f}-{args.fmax:.0f} Hz (time flows down)\n")
    for i, row in enumerate(rows):
        print(f"{i * group * hop_s:6.1f}s " + "".join(cell(v) for v in row))
        if args.live:
            time.sleep(1.0 / args.rows_per_sec)

    peak = find_peak_frequency(S, freqs, args.fmin, args.fmax)
    band = (max(args.fmin, peak - 50), peak + 50)
    energy = band_energy(S, freqs, *band)
    segs = detect_segments(energy, times)
    print(f"\nStrongest frequency: {peak:.0f} Hz")
    print(f"Detected {len(segs)} ON segments around that frequency:")
    for s, e in segs:
        print(f"  {s:6.2f}s -> {e:6.2f}s  ({e - s:.2f}s)")


if __name__ == "__main__":
    main()
