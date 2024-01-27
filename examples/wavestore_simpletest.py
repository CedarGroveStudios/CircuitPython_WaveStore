# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
#
# wavestore_simpletest.py

import gc
import time
import board
import displayio
import synthio
import adafruit_ili9341

import ulab.numpy as np
import bitmaptools

from adafruit_display_shapes.polygon import Polygon

# import audiobusio
# import audiomixer
from cedargrove_wavebuilder import WaveBuilder, WaveShape
from cedargrove_waveviz import WaveViz
from cedargrove_waveviz_helper import waveviz_helper
from cedargrove_wavestore import WaveStore

# Instantiate WaveStore to manage SD card contents
w_store = WaveStore(board.SPI(), board.D20, debug=False)

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
# harp_icon = WaveViz(harp.wave_table, (10, 10), (128, 128))
harp_icon = waveviz_helper(harp.wave_table, (10, 10), (128, 128), output="bitmap")

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
chime_icon = WaveViz(chime.wave_table, (160, 10), (128, 128))

string_envelope = synthio.Envelope(
    attack_time=0.0001,
    attack_level=1.0,
    decay_time=0.977,
    release_time=0.200,
    sustain_level=0.500,
)

# Test 1: Get the SD directory and print list to REPL
print("Test 1: Get the SD directory and print list to REPL")
print(f"SD directory: {w_store.get_catalog()}")
print("     completed")

# Test 2: Write bitmap image to a file
print("Test 2: Write bitmap image to a file")
"""w_store.write_bitmap(
    harp_icon.bitmap, harp_icon.palette, filename="harp_icon.bmp", overwrite=True
)"""
w_store.write_bitmap(harp_icon[0], harp_icon[1], filename="harp_icon.bmp", overwrite=True)
print("     completed")

# Test 3: Read and display saved bitmap
print("Test 3: Read and display saved bitmap")
splash.append(w_store.read_bitmap("harp_icon.bmp"))
print("     completed")

# Test 4: Add second icon and save entire screen to a file
print("Test 4: Add second icon and save entire screen to a file")
splash.append(chime_icon)
w_store.write_screen(display, "screenshot.bmp", overwrite=True)
print("     completed")

# Test 5: Clear the screen and read and display saved screenshot
print("Test 5: Clear the screen and read and display saved screenshot")
splash.pop()
splash.pop()
time.sleep(1)  # Wait for a moment to show blank screen
splash.append(w_store.read_bitmap("screenshot.bmp"))
print("     completed")

# Test 6: Write wave table to a file

# Test 7: Read wave table as memoryview object from a file and display

# Test 8: Read wave table as ulab array from a file and display

# Test 9: Write envelope object to a file

# Test 10: Read envelope object from a file

# Test 11: Write filter object to a file

# Test 12: Read filter object from file

# Test 13: Display wave table bitmap with transparency
splash.append(displayio.TileGrid(harp_icon[0], pixel_shader=harp_icon[1], x=100, y=100))

# All tests completed
print("*** All tests completed ***")
print(f"memfree delta: {gc.mem_free() - m0}")
print(f"time delta: {time.monotonic() - t0}")
while True:
    pass

"""
# Synth playback code
# Configure synthesizer for I2S output on a Feather S2
audio_output = audiobusio.I2SOut(
    bit_clock=board.D19, word_select=board.D18, data=board.D17, left_justified=False
)
mixer = audiomixer.Mixer(
    sample_rate=SAMPLE_RATE, buffer_size=4096, voice_count=1, channel_count=1
)
audio_output.play(mixer)
mixer.voice[0].level = 0.50

synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)
mixer.play(synth)

note_1 = synthio.Note(440, envelope=tone_envelope, waveform=wave.wave_table)

notes = [261.626, 329.628, 391.995, 523.251]  # Cmaj arpeggio

while True:
    for note in notes:
        note_1.frequency = note * 1.0
        synth.press(note_1)
        time.sleep(0.1)
        synth.release(note_1)
        time.sleep(0.125)
    time.sleep(1)
"""
