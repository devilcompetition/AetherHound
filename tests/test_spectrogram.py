import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dsp"))

from spectrogram import (band_energy, compute_spectrogram, detect_segments,
                         find_peak_frequency)

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
