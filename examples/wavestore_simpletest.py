# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# wavestore_simpletest.py

import gc
import time
import board
from math import log, cos, sin, sqrt, pi
import displayio
import synthio
import adafruit_ili9341

from cedargrove_wavebuilder import WaveBuilder, WaveShape
from cedargrove_waveviz import WaveViz
from cedargrove_wavestore import WaveStore

DEBUG = False
SAMP_RATE = 22_050  # samples per second

synth = synthio.Synthesizer(sample_rate=SAMP_RATE)

# Instantiate WaveStore to manage SD card contents
w_store = WaveStore(board.SPI(), board.D20, debug=DEBUG)

# Instantiate the 2.4-inch TFT Wing attached to FeatherS2
displayio.release_displays()  # Release display resources
display_bus = displayio.FourWire(
    board.SPI(), command=board.D6, chip_select=board.D5, reset=None
)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
display.rotation = 0
splash = displayio.Group()
display.root_group = splash

m0 = gc.mem_free()
t0 = time.monotonic()

# Create two waveforms, icons, and an envelope for the tests
harp_tone = [
    (WaveShape.Sine, 1.00, 0.10),
    (WaveShape.Sine, 2.00, 0.48),
    (WaveShape.Sine, 3.00, 0.28),
    (WaveShape.Sine, 4.00, 0.02),
    (WaveShape.Sine, 5.00, 0.12),
]
harp = WaveBuilder(oscillators=harp_tone, table_length=512)
harp_icon = WaveViz(harp.wave_table, 10, 10, 128, 128)

chime_tone = [
    (WaveShape.Sine, 1.00, -0.60),
    (WaveShape.Sine, 2.76, 0.20),
    (WaveShape.Sine, 5.40, 0.10),
    (WaveShape.Sine, 8.93, 0.07),
    (WaveShape.Sine, 11.34, 0.01),
    (WaveShape.Sine, 18.64, 0.01),
    (WaveShape.Sine, 31.87, 0.01),
]
chime = WaveBuilder(oscillators=chime_tone, table_length=512)
chime_icon = WaveViz(chime.wave_table, 160, 10, 128, 128)

string_envelope = synthio.Envelope(
    attack_time=0.0001,
    attack_level=1.0,
    decay_time=0.977,
    release_time=0.200,
    sustain_level=0.500,
)

# Create three filters for testing
lp_filter = synth.low_pass_filter(880)
hp_filter = synth.high_pass_filter(440)
bp_filter = synth.band_pass_filter(440)

print(f"lp_filter: {lp_filter}")
print(lp_filter[0])
print([param for param in lp_filter])
print(f"hp_filter: {hp_filter}")
print(f"bp_filter: {bp_filter}")


# audio cookbook: https://github.com/shepazu/Audio-EQ-Cookbook/blob/master/Audio-EQ-Cookbook.txt
# w0 = 2*pi*f0/Fs  # ???

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

# Test 1: Get the SD directory and print list to REPL
print("\nTest 1: Get the SD directory and print list to REPL")
print(f"SD directory: {w_store.get_catalog()}")
print(" completed")

# Test 2: Write bitmap image to a file
print("\nTest 2: Write bitmap image to a file")
w_store.write_bitmap(
    harp_icon.bitmap, harp_icon.pixel_shader, filename="harp_icon.bmp", overwrite=True
)
print(" completed")

# Test 3: Read and display saved bitmap
print("\nTest 3: Read and display saved bitmap")
splash.append(w_store.read_bitmap("harp_icon.bmp"))
print(" completed")

# Test 4: Add second icon and save entire screen to a file
print("\nTest 4: Add second icon and save entire screen to a file")
splash.append(chime_icon)
w_store.write_screen(display, "screenshot.bmp", overwrite=True)
print(" completed")

# Test 5: Clear the screen and read and display saved screenshot
print("\nTest 5: Clear the screen and read and display saved screenshot")
splash.pop()
splash.pop()
time.sleep(1)  # Wait for a moment to show blank screen
splash.append(w_store.read_bitmap("screenshot.bmp"))
print(" completed")

# Test 6: Write wave table to a file
print("\nTest 6: Write wave table to a file")
print(harp_icon.wave_table)
w_store.write_wavetable(
    harp_icon.wave_table, "harp.wav", samp_rate=SAMP_RATE, overwrite=True
)
print(" completed")

# Test 7: Read wavetable as memory_view object from a file and display
print("\nTest 7: Read wavetable as memory_view object from a file and display")
wave_table = w_store.read_wavetable("harp.wav")
print(f"w_store.read_wavetable: {wave_table}")
harp_icon.wave_table = w_store.read_wavetable("harp.wav")
print(" completed")

# Test 8: Read wave table as ulab array from a file and display

# Test 9: Write envelope object to a file
print("\nTest 9: Write envelope object to a file")
w_store.write_envelope(string_envelope, "string.env", True)
print(" completed")

# Test 10: Read envelope object from a file
print("\nTest 10: Read envelope object from a file")
new_env = w_store.read_envelope("string.env")
print(" completed")

# Test 11: Write filter object to a file

# Test 12: Read filter object from file

# Test 13: Display wave table bitmap with transparency
print("\nTest 13: Display wave table bitmap with transparency")
splash.append(
    displayio.TileGrid(
        harp_icon.bitmap, pixel_shader=harp_icon.pixel_shader, x=100, y=100
    )
)
print(" completed")

# All tests completed
print("\n*** All tests completed ***")
print(f"mem_free delta: {gc.mem_free() - m0}")
print(f"time delta: {time.monotonic() - t0}")
while True:
    pass
