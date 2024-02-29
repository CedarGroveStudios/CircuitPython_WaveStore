# SPDX-FileCopyrightText: Copyright (c) 2024 @todbot
# SPDX-License-Identifier: MIT

from ulab import numpy as np
import adafruit_wave


def lerp(value_0, value_1, blend):
    """Mix between values value_0 and value_1 using linear interpolation. Works
    with numpy arrays, too. blend (t) ranges 0 to 1 (inclusive).
    = ((1 - blend) * value_0) + (blend * value_1) ?"""
    return (1 - blend) * value_0 + blend * value_1


class WaveTable:
    """From @todbot's wave table hints:
    https://github.com/todbot/circuitpython-synthio-tricks
    Thanks to @todbot and @jepler."""

    def __init__(self, filepath, wave_len=256):
        self.w = adafruit_wave.open(filepath)
        self.wave_len = wave_len  # how many samples in each wave
        if self.w.getsampwidth() != 2 or self.w.getnchannels() != 1:
            raise ValueError("unsupported WAV format")
        # create an empty buffer to copy into
        self.waveform = np.zeros(wave_len, dtype=np.int16)
        self.num_waves = self.w.getnframes() / self.wave_len

    def set_wave_pos(self, pos):
        """Pick where in wave table to be, morphing between waves."""
        pos = min(max(pos, 0), self.num_waves - 1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        wave_a = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        wave_b = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave_a and wave_b
        self.waveform[:] = lerp(wave_a, wave_b, pos_frac)  # mix wave_a and wave_b

    """
    Usage example:
    wavetable = WaveTable("BRAIDS02.WAV", 256)  # from http://waveeditionline.com/index-17.html
    note = synthio.Note(frequency=220, waveform=wavetable.waveform
    synth.press(note)  # start an oscillator going

    # scan through the wavetable, morphing through each one
    i = 0
    di = 0.1  # how fast to scan
    while True:
        i = i + di
        if i <=0 or i >= wavetable.num_waves:
        di = -di
    wavetable.set_wave_pos(i)
    time.sleep(0.001)
    """
