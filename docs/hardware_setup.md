# Hardware Setup

## What I used
- Microphone: [laptop built-in mic, model if known]
- Recording script: capture/record_audio.py (pyaudio)
- Sample rate: 44100 Hz, mono, 16-bit
- Computer: [laptop model, OS: Windows]

## What I did not use
- No SDR (HackRF/RTL-SDR) and no ultrasonic microphone were available.
- The RF channel is covered through research only.
- Because no real fan recording was used for testing, the detector was
  tested on a simulated Morse tone from mock_malware/make_test_signal.py.

## How the test signal is made
mock_malware/fan_pulse.py loads the CPU in a Morse pattern so the fan speed
changes. make_test_signal.py creates a similar pattern as a clean tone for
repeatable tests.

## Limitations
- Laptop microphones pick up low frequencies poorly and add noise.
- Fan speed changes slowly, so pulses must be at least about 1 to 2 seconds.
