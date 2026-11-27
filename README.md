# AetherHound: Air-Gapped RF & Acoustic Covert Channel Detector

**Infotact Solutions | Cyber Security Internship | Project Ref: ITS/CS/1215**

## Overview

Air-gapped servers have no network connection, but malware running on them can
still leak data through physical side channels. For example, it can modulate CPU
load so the cooling fan speed changes in a Morse-like pattern, or generate
electromagnetic emissions that a nearby receiver can pick up.

AetherHound monitors the acoustic (and, in the full design, RF) environment of a
server room and flags structured, non-random signals that may indicate a covert
channel.

## Current Status (mid-review)

| Area | Status |
|---|---|
| Benign mock malware (CPU-load Morse pulser) | Done |
| Microphone recording script | Done |
| FFT spectrogram, peak frequency, ON/OFF segment detection | Done |
| Periodicity check (structured on/off pattern: yes/no) | Done |
| Terminal waterfall display with detection summary | Done |
| Simulated Morse test signal generator | Done |
| Unit tests (Morse helper and DSP code) | Done |
| Autoencoder anomaly model (PyTorch) | Planned (Week 3) |
| Alerting (red flash, buzzer) and logging | Planned (Weeks 3-4) |
| C++ acceleration of DSP math | Planned (Week 4) |
| Live RF capture with an SDR | Not available, see Limitations |

## How It Works

1. **Capture:** A microphone is recorded to a WAV file (`capture/record_audio.py`).
   For repeatable tests, `mock_malware/make_test_signal.py` generates a simulated
   Morse-keyed tone with background noise.
2. **DSP pipeline:** `dsp/spectrogram.py` loads the WAV, runs a short-time FFT to
   build a spectrogram, finds the strongest frequency and measures the signal
   level in that band over time.
3. **Pattern detection:** The band level is thresholded into ON/OFF segments.
   `check_pattern()` then groups the ON durations. A keyed signal such as Morse
   has only a few distinct durations (dots and dashes), while random noise does
   not, so a structured pattern is reported as a possible covert channel.
4. **Terminal UI:** `cli/waterfall.py` prints a colour waterfall (time flows down,
   frequency goes across), the strongest frequency, the detected segments and the
   pattern check result.

## Architecture

```
mic / simulated signal -> capture/ -> dsp/ -> cli/ (waterfall + detection)
                                       ^
                       mock_malware/ (benign test signal)

Planned: dsp/ -> ml/ (autoencoder) -> cli/ (alerts + logs)
```

## Repository Structure

| Folder | Purpose |
|---|---|
| `capture/` | `record_audio.py`: record microphone audio to WAV |
| `mock_malware/` | `morse.py`, `fan_pulse.py` (benign CPU-load pulser), `make_test_signal.py` (simulated tone) |
| `dsp/` | `spectrogram.py`: FFT spectrogram, peak frequency, ON/OFF segments, pattern check |
| `cli/` | `waterfall.py`: terminal waterfall and detection summary |
| `ml/` | Autoencoder model, training and evaluation (planned) |
| `tests/` | Unit tests |
| `data/` | Small sample datasets only (large recordings are git-ignored) |
| `docs/` | Documentation, reports and notes |

## Setup

```bash
git clone https://github.com/devilcompetition/AetherHound.git
cd AetherHound
git checkout air2
pip install -r requirements.txt
```

## Usage

Create a simulated test signal (no hardware needed):

```bash
cd mock_malware
python make_test_signal.py --message SOS --freq 1000 --unit 0.2 --out ../data/samples/sim_sos.wav
cd ..
```

Run the waterfall and detector:

```bash
python cli/waterfall.py data/samples/sim_sos.wav --fmin 500 --fmax 1500
```

Expected result for the SOS sample: 9 ON segments (3 short, 3 long, 3 short) and
a line saying a structured on/off pattern was found.

Record from a microphone:

```bash
python capture/record_audio.py --list
python capture/record_audio.py --seconds 10 --out recording.wav
```

Preview the mock malware without generating any load:

```bash
python mock_malware/fan_pulse.py --message SOS --dry-run
```

Run the tests:

```bash
pytest tests/
```

## Limitations

- **Software only:** no SDR (HackRF/RTL-SDR) or ultrasonic microphone was used.
  The RF channel is covered through research only, and live RF capture is out of
  scope for this version.
- **Simulated test signal:** most testing uses a clean simulated tone. Real fan
  recordings are noisier, so the thresholds in `check_pattern()` (`tol`,
  `min_duration`) may need tuning on real data.
- **Simple detector:** the current detector is threshold-based. The machine
  learning anomaly model is planned for Week 3.
- Fan speed changes slowly, so real pulses need to be at least 1 to 2 seconds long.

## Team

Each member works on their own branch of this shared repository. The Team Lead
merges reviewed work into `main`.

| Name | Role | Branch |
| Team Lead | Coordination, hardware, repo and final merge | `main` |
| Mandodari Raju | Member 2: DSP pipeline, CLI waterfall, detection | `air2` |
| [Name] | Member 3: [role] | `air3` |
| [Name] | Member 4: [role] | `air4` |

## Safety Note

The mock malware in this project is a benign test tool. It only varies CPU load
on the developer's own machine to generate a known test signal. It does not
exfiltrate data or affect other systems.

## Deliverables

Source code, project documentation, project report, presentation (PPT), model
evaluation results, and final demonstration.
