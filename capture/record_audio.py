"""Record audio from a microphone to a WAV file.

Usage:
    python record_audio.py --list
    python record_audio.py --seconds 10 --out ../data/raw/normal_10s.wav
    python record_audio.py --seconds 10 --device 1 --rate 48000
"""
import argparse
import wave

import pyaudio

CHUNK = 1024


def list_devices():
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"[{i}] {info['name']}  (rate {int(info['defaultSampleRate'])} Hz)")
    pa.terminate()


def record(seconds, out_path, rate=44100, channels=1, device=None):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=channels, rate=rate,
                     input=True, input_device_index=device,
                     frames_per_buffer=CHUNK)
    print(f"Recording {seconds}s at {rate} Hz ...")
    frames = [stream.read(CHUNK, exception_on_overflow=False)
              for _ in range(int(rate / CHUNK * seconds))]
    stream.stop_stream()
    stream.close()
    sample_width = pa.get_sample_size(pyaudio.paInt16)
    pa.terminate()

    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))
    print(f"Saved {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Record microphone audio to WAV")
    ap.add_argument("--list", action="store_true", help="list input devices")
    ap.add_argument("--seconds", type=float, default=10)
    ap.add_argument("--out", default="recording.wav")
    ap.add_argument("--rate", type=int, default=44100)
    ap.add_argument("--channels", type=int, default=1)
    ap.add_argument("--device", type=int, default=None)
    args = ap.parse_args()
    if args.list:
        list_devices()
    else:
        record(args.seconds, args.out, args.rate, args.channels, args.device)


if __name__ == "__main__":
    main()
