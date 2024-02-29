# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

from math import log, sqrt, cos, sin, pi
import synthio

SAMP_RATE = 22_050  # samples per second

synth = synthio.Synthesizer(sample_rate=SAMP_RATE)

# Create three filters for testing
lp_filter = synth.low_pass_filter(880)
hp_filter = synth.high_pass_filter(440)
bp_filter = synth.band_pass_filter(440)

print(f"lp_filter: {lp_filter}")
print(lp_filter[0])
print(list(lp_filter))
print(f"hp_filter: {hp_filter}")
print(f"bp_filter: {bp_filter}")


# audio cookbook: https://github.com/shepazu/Audio-EQ-Cookbook/blob/master/Audio-EQ-Cookbook.txt
# w0 = 2*pi*f0/Fs  # ???

# pylint: disable=line-too-long
# from https://www.musicdsp.org/en/latest/Analysis/186-frequency-response-from-biquad-coefficients.html
# w = frequency (0 < w < PI)
# y = 20*log((sqrt(square(a0*square(cos(w))-a0*square(sin(w))+a1*cos(w)+a2)+square(2*a0*cos(w)*sin(w)+a1*(sin(w))))/
#          sqrt(square(square(cos(w))-square(sin(w))+b1*cos(w)+b2)+square(2*cos(w)*sin(w)+b1*(sin(w))))));

# square(x) = x*x


def sq(x):
    return x * x


def biquad_y(w0):
    # w0: frequency for transfer function; 0 to pi ???
    y = 20 * log(
        (
            sqrt(
                sq(a0 * sq(cos(w0)) - a0 * sq(sin(w0)) + a1 * cos(w0) + a2)
                + sq(2 * a0 * cos(w0) * sin(w) + a1 * (sin(w0)))
            )
            / sqrt(
                sq(sq(cos(w0)) - sq(sin(w0)) + b1 * cos(w0) + b2)
                + sq(2 * cos(w0) * sin(w0) + b1 * (sin(w0)))
            )
        )
    )
    return y


a0 = 1
a1 = lp_filter[0]
a2 = lp_filter[1]
b0 = lp_filter[2]
b1 = lp_filter[3]
b2 = lp_filter[4]

for i in range(1, 100, 4):
    w = pi / i  # ???
    y0 = biquad_y(w)
    print(f"i, w, y0 : {i:03.0f} {w:08.4f} {y0:+08.4f}")

while True:
    pass
