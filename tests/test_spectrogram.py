import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dsp"))

from spectrogram import (band_energy, check_pattern, compute_spectrogram,
                         detect_segments, find_peak_frequency)

RATE = 8000


def _tone(freq, seconds=1.0):
    t = np.arange(int(RATE * seconds)) / RATE
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def test_peak_frequency():
    freqs, times, S = compute_spectrogram(_tone(1000), RATE)
    assert abs(find_peak_frequency(S, freqs) - 1000) < 10


def test_shapes():
    freqs, times, S = compute_spectrogram(_tone(500), RATE, n_fft=1024, hop=256)
    assert S.shape == (len(times), len(freqs))


def test_detect_one_burst():
    x = np.concatenate([np.zeros(RATE), _tone(1000, 1.0), np.zeros(RATE)])
    freqs, times, S = compute_spectrogram(x, RATE)
    energy = band_energy(S, freqs, 900, 1100)
    segs = detect_segments(energy, times)
    assert len(segs) == 1
    assert 0.8 < segs[0][0] < 1.3 and 1.7 < segs[0][1] < 2.3


def test_pattern_detected_for_keyed_signal():
    unit = int(RATE * 0.3)
    parts = [np.zeros(RATE)]
    for units in [1, 1, 1, 3, 3, 3, 1, 1, 1]:
        parts += [_tone(1000, units * 0.3), np.zeros(unit)]
    x = np.concatenate(parts + [np.zeros(RATE)])
    freqs, times, S = compute_spectrogram(x, RATE)
    segs = detect_segments(band_energy(S, freqs, 900, 1100), times)
    structured, groups = check_pattern(segs)
    assert structured
    assert len(groups) == 2


def test_pattern_not_detected_for_noise():
    for seed in range(5):
        rng = np.random.default_rng(seed)
        x = (0.1 * rng.standard_normal(RATE * 5)).astype(np.float32)
        freqs, times, S = compute_spectrogram(x, RATE)
        segs = detect_segments(band_energy(S, freqs, 900, 1100), times)
        structured, _ = check_pattern(segs)
        assert not structured
