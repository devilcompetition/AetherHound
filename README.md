# AetherHound: Air-Gapped RF & Acoustic Covert Channel Detector

**Infotact Solutions | Cyber Security Internship | Project Ref: ITS/CS/1215**

## Overview

Air-gapped servers have no network connection, but malware running on them can
still leak data through physical side channels. For example, it can modulate CPU
load so the cooling fan speed changes in a Morse-like pattern, or generate
electromagnetic emissions that a nearby receiver can pick up.

AetherHound is a hardware-software system that monitors a server room's radio
frequency (RF) and acoustic environment, learns what "normal" looks like, and
flags anomalous, structured signals that may indicate a covert channel.

## How It Works

1. **Capture:** A software defined radio (SDR) records RF spectrum data and a
   microphone records room audio.
2. **DSP pipeline:** Signals are filtered and converted to spectrograms using
   Fast Fourier Transforms (FFT).
3. **Anomaly detection:** An autoencoder neural network is trained only on
   normal server emissions. Signals it cannot reconstruct well (high
   reconstruction error) are flagged as anomalous.
4. **Terminal UI:** A curses/rich based CLI shows the live spectrum waterfall,
   alerts on anomalies, and logs the timestamp and frequency of each detection.

## Architecture

```
SDR + Microphone -> capture/ -> dsp/ -> ml/ -> cli/ (alerts + logs)
                                  ^
                        mock_malware/ (benign test signal)
```

## Repository Structure

| Folder | Purpose |
|---|---|
| `capture/` | Scripts to record raw RF and audio data |
| `mock_malware/` | Benign script that pulses CPU load in a Morse-like pattern for testing |
| `dsp/` | Filtering, FFT and spectrogram generation |
| `ml/` | Autoencoder model, training and evaluation |
| `cli/` | Terminal dashboard and alerting |
| `data/` | Small sample datasets only (large recordings are git-ignored) |
| `docs/` | Documentation, reports and diagrams |

## Tech Stack

Python, GNU Radio, NumPy/SciPy, PyTorch, pyaudio, rtlsdr/HackRF, curses/rich,
C++ (for performance-critical DSP in Week 4)

## Project Plan

| Week | Focus |
|---|---|
| 1 | Hardware setup, raw RF/audio capture scripts, mock malware script |
| 2 | DSP flowgraph, FFT spectrograms, live terminal waterfall UI |
| Mid Review | Isolate the mock malware's frequency spike; UI at 30+ FPS |
| 3 | Train autoencoder on normal data; alerting logic (red flash and buzzer) |
| 4 | C++ optimization, false-positive reduction, logging, final polish |
| Final Review | Working covert channel detector with CLI dashboard |

## Setup

```bash
git clone https://github.com/devilcompetition/AetherHound.git
cd AetherHound
pip install -r requirements.txt
```

## Team

| Name | Role | Branch |
|---|---|---|
| Mandodari Raju | [Role] | [branch-name] |

## Safety Note

The mock malware in this project is a benign test tool. It only varies CPU load
on the developer's own machine to generate a known test signal. It does not
exfiltrate data or affect other systems.

## Deliverables

Source code, project documentation, project report, presentation (PPT), model
evaluation results, and final demonstration.
