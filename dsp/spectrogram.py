"""FFT / spectrogram pipeline for AetherHound (Week 2).

Pure NumPy so it runs anywhere. Steps:
  load_wav -> compute_spectrogram -> band_energy -> detect_segments
"""
import wave

import numpy as np


def load_wav(path):
    """Load a 16-bit WAV file. Returns (samples in [-1, 1], sample_rate)."""
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if width != 2:
        raise ValueError("Only 16-bit WAV files are supported")
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        x = x.reshape(-1, channels).mean(axis=1)
    return x, rate


def compute_spectrogram(x, rate, n_fft=2048, hop=512):
    """Short-time FFT. Returns (freqs in Hz, times in s, S in dB[time, freq])."""
    if len(x) < n_fft:
        raise ValueError("Signal shorter than one FFT window")
    window = np.hanning(n_fft)
    n_frames = 1 + (len(x) - n_fft) // hop
    frames = np.stack([x[i * hop:i * hop + n_fft] * window for i in range(n_frames)])
    mag = np.abs(np.fft.rfft(frames, axis=1))
    S = 20 * np.log10(mag + 1e-10)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / rate)
    times = (np.arange(n_frames) * hop + n_fft / 2) / rate
    return freqs, times, S


def find_peak_frequency(S, freqs, fmin=20.0, fmax=None):
    """Frequency (Hz) with the highest average level inside [fmin, fmax]."""
    fmax = fmax if fmax is not None else freqs[-1]
    mask = (freqs >= fmin) & (freqs <= fmax)
    mean_spec = S[:, mask].mean(axis=0)
    return float(freqs[mask][np.argmax(mean_spec)])


def band_energy(S, freqs, fmin, fmax):
    """Mean level (dB) per time frame inside a frequency band."""
    mask = (freqs >= fmin) & (freqs <= fmax)
    return S[:, mask].mean(axis=1)


def detect_segments(energy, times, threshold=None):
    """Find ON segments where band energy is above threshold.

    Returns a list of (start_s, end_s). Default threshold is halfway
    between the median level and the maximum level.
    """
    if threshold is None:
        med = float(np.median(energy))
        threshold = med + 0.5 * (float(energy.max()) - med)
    on = energy > threshold
    segments, start = [], None
    for t, flag in zip(times, on):
        if flag and start is None:
            start = t
        elif not flag and start is not None:
            segments.append((float(start), float(t)))
            start = None
    if start is not None:
        segments.append((float(start), float(times[-1])))
    return segments


def check_pattern(segments, min_segments=3, tol=0.3, min_duration=0.15):
    """Simple yes/no check: do the ON segments look like a keyed signal?

    A deliberate covert channel (for example Morse) uses only a few distinct
    ON durations (dot and dash). Random noise gives many different durations.
    ON durations are grouped when they are within `tol` (relative) of the
    group mean. The pattern counts as structured when there are at least
    `min_segments` segments and at most 3 duration groups. Segments shorter
    than `min_duration` seconds are ignored, because random noise produces
    many very short blips.

    Returns (is_structured, groups) where groups is a list of
    (mean_duration_s, count).
    """
    durations = sorted(e - s for s, e in segments if e - s >= min_duration)
    if len(durations) < min_segments:
        return False, []
    groups = [[durations[0]]]
    for d in durations[1:]:
        mean = sum(groups[-1]) / len(groups[-1])
        if abs(d - mean) / mean <= tol:
            groups[-1].append(d)
        else:
            groups.append([d])
    summary = [(sum(g) / len(g), len(g)) for g in groups]
    return len(groups) <= 3, summary
