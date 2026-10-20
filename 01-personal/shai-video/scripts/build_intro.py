#!/usr/bin/env python3
"""Build the podcast intro: radio-processed voiceover over a generated music bed.

Usage:
    python build_intro.py --voice raw/audio/intro-voice.wav --out intro.mp3

The voice file is the recording of the speaker (WAV or MP3). The script does
not contain personal media. Requires ffmpeg on PATH, or the imageio-ffmpeg package.
"""
import argparse
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 12.0
BPM = 124
VOICE_DELAY_MS = 500


def find_ffmpeg(explicit):
    if explicit:
        return explicit
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def make_bed(path):
    beat = 60 / BPM
    n = int(SR * DUR)
    out = np.zeros(n)
    rng = np.random.default_rng(3)

    def add(sig, start):
        i0 = int(start * SR)
        if i0 < n:
            m = min(len(sig), n - i0)
            out[i0:i0 + m] += sig[:m]

    def stab(freq, length):
        tt = np.arange(int(length * SR)) / SR
        s = sum(np.sign(np.sin(2 * np.pi * freq * k * tt)) / k for k in (1, 2, 3, 4, 5))
        return s * np.exp(-tt * 6) * 0.12

    def bass(freq, length):
        tt = np.arange(int(length * SR)) / SR
        return np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 4) * 0.35

    def kick():
        tt = np.arange(int(0.22 * SR)) / SR
        f = 130 * np.exp(-tt * 22) + 48
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 16) * 0.7

    def hat(open_=False):
        m = int((0.12 if open_ else 0.035) * SR)
        tt = np.arange(m) / SR
        return rng.standard_normal(m) * np.exp(-tt * (25 if open_ else 110)) * 0.07

    # Chord roots and voicings for the four-bar loop: C - G - Am - F
    progression = [
        (261.63, [261.63, 329.63, 392.0]),
        (196.0, [196.0, 246.94, 293.66]),
        (220.0, [220.0, 261.63, 329.63]),
        (174.61, [174.61, 220.0, 261.63]),
    ]
    bar = 4 * beat
    for b in range(int(DUR / bar) + 1):
        root, chord = progression[b % 4]
        for k in range(8):
            add(stab(chord[k % 3], beat * 0.4), b * bar + k * beat / 2 + beat / 2)
            add(bass(root / 2, beat * 0.45), b * bar + k * beat / 2)
    for k in range(int(DUR / beat)):
        start = k * beat
        if start >= DUR - 0.3:
            break
        if k >= 2:
            add(kick(), start)
            for s in range(4):
                add(hat(), start + s * beat / 4)
            add(hat(True), start + beat / 2)

    fade_in = int(0.3 * SR)
    out[:fade_in] *= np.linspace(0, 1, fade_in)
    fade_out = int(1.6 * SR)
    out[-fade_out:] *= np.linspace(1, 0, fade_out)
    out = out / np.max(np.abs(out)) * 0.9
    pcm = (np.stack([out, out], axis=1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def build(voice, out, ffmpeg):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bed = tmp / "bed.wav"
        radio = tmp / "voice_radio.wav"
        make_bed(bed)
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(voice),
             "-af", f"highpass=f=170,lowpass=f=5500,"
                    f"acompressor=threshold=-20dB:ratio=4:attack=5:release=80,"
                    f"volume=4dB,adelay={VOICE_DELAY_MS}|{VOICE_DELAY_MS},apad=whole_dur={DUR}",
             "-ar", str(SR), "-ac", "2", str(radio)])
        mix = ("[1:a]asplit=2[vo][sc];"
               "[0:a][sc]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=300[bed];"
               "[bed][vo]amix=inputs=2:duration=first:normalize=0,"
               f"afade=t=out:st={DUR - 1.6}:d=1.6,loudnorm=I=-14:TP=-1.5:LRA=7[out]")
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(bed), "-i", str(radio),
             "-filter_complex", mix, "-map", "[out]", "-t", str(DUR),
             "-ar", str(SR), "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k", str(out)])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--voice", required=True, type=Path, help="voiceover recording (WAV or MP3)")
    parser.add_argument("--out", required=True, type=Path, help="output MP3 path")
    parser.add_argument("--ffmpeg", default=None, help="path to ffmpeg binary (optional)")
    args = parser.parse_args()
    if not args.voice.is_file():
        raise SystemExit(f"voice file not found: {args.voice}")
    build(args.voice, args.out, find_ffmpeg(args.ffmpeg))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
