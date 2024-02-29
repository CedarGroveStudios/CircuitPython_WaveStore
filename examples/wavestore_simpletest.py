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

from cedargrove_wavebuilder import WaveBuilder, WaveShape
from cedargrove_waveviz import WaveViz
from cedargrove_wavestore import WaveStore

DEBUG = False
SAMP_RATE = 22_050  # samples per second
TEST_LIST = list(range(0, 20))  # List of tests to perform

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

# pylint: disable=no-member
m0 = gc.mem_free()
t0 = time.monotonic()

# Create two waveforms, icons, and two envelopes for the tests
harp_tone = [
    (WaveShape.Sine, 1.00, 0.10),
    (WaveShape.Sine, 2.00, 0.48),
    (WaveShape.Sine, 3.00, 0.28),
    (WaveShape.Sine, 4.00, 0.02),
    (WaveShape.Sine, 5.00, 0.12),
]
harp = WaveBuilder(oscillators=harp_tone, table_length=512)
harp_icon = WaveViz(harp.wave_table, 10, 10, 64, 64)

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
chime_icon = WaveViz(chime.wave_table, 10, 80, 64, 64)

string_envelope = synthio.Envelope(
    attack_time=0.0001,
    attack_level=1.0,
    decay_time=0.977,
    release_time=0.200,
    sustain_level=0.500,
)
string_env_icon = WaveViz(string_envelope, 80, 26, 64, 32)

chime_steel_envelope = synthio.Envelope(
    attack_time=0.02,
    attack_level=1.0,
    decay_time=0.1,
    release_time=2.0,
    sustain_level=0.0,
)
chime_steel_env_icon = WaveViz(chime_steel_envelope, 80, 96, 64, 32)

# Start testing

# Test 1: Get the SD directory and print list to REPL
if 1 in TEST_LIST:
    print("\nTest 1: Get the SD directory and print list to REPL")
    print(f"SD directory: {w_store.get_catalog()}")
    print(" completed")

# Test 2: Write waveform bitmap images to files
if 2 in TEST_LIST:
    print("\nTest 2: Write bitmap image to a file")
    w_store.write_bitmap(
        harp_icon.bitmap,
        harp_icon.pixel_shader,
        filename="harp_icon.bmp",
        overwrite=True,
    )
    w_store.write_bitmap(
        chime_icon.bitmap,
        chime_icon.pixel_shader,
        filename="chime_steel_icon.bmp",
        overwrite=True,
    )
    print(" completed")

# Test 3: Read and display saved bitmap
if 3 in TEST_LIST:
    print("\nTest 3: Read and display saved bitmap")
    new_bitmap = w_store.read_bitmap("harp_icon.bmp")
    new_bitmap.x = 10
    new_bitmap.y = 10
    splash.append(new_bitmap)
    print(" completed")

# Test 4: Add second icon and envelopes; save entire screen to a file
if 4 in TEST_LIST:
    print("\nTest 4: Add second icon and envelopes; save entire screen to a file")
    splash.append(chime_icon)
    splash.append(string_env_icon)
    splash.append(chime_steel_env_icon)
    w_store.write_screen(display, "screenshot.bmp", overwrite=True)
    print(" completed")

# Test 5: Clear the screen and read and display saved screenshot
if 5 in TEST_LIST:
    print("\nTest 5: Clear the screen and read and display saved screenshot")
    splash.pop()
    splash.pop()
    time.sleep(1)  # Wait for a moment to show blank screen
    splash.append(w_store.read_bitmap("screenshot.bmp"))
    print(" completed")

# Test 6: Write wave tables to files
if 6 in TEST_LIST:
    print("\nTest 6: Write wave tables to files")
    print(harp_icon.wave_table)
    w_store.write_wavetable(
        harp_icon.wave_table, "harp.wav", samp_rate=SAMP_RATE, overwrite=True
    )
    print(chime_icon.wave_table)
    w_store.write_wavetable(
        chime_icon.wave_table, "chime_steel.wav", samp_rate=SAMP_RATE, overwrite=True
    )
    print(" completed")

# Test 7: Read wavetable as memory_view object from a file and display
if 7 in TEST_LIST:
    print("\nTest 7: Read wavetable as memory_view object from a file and display")
    wave_table = w_store.read_wavetable("harp.wav")
    print(f"w_store.read_wavetable: {wave_table}")
    harp_icon.wave_table = w_store.read_wavetable("harp.wav")
    print(" completed")

# Test 8: Read wave table as ulab array from a file and display
if 8 in TEST_LIST:
    pass

# Test 9: Write envelope objects to files
if 9 in TEST_LIST:
    print("\nTest 9: Write envelope objects to files")
    w_store.write_envelope(string_envelope, "string.env", overwrite=True)
    w_store.write_envelope(chime_steel_envelope, "chime_steel.env", overwrite=True)
    print(" completed")

# Test 10: Read envelope object from a file
if 10 in TEST_LIST:
    print("\nTest 10: Read envelope object from a file")
    new_env = w_store.read_envelope("string.env")
    print(" completed")

# Test 11: Write envelope bitmap image to a file
if 11 in TEST_LIST:
    print("\nTest 11: Write envelope bitmap image to a file")
    w_store.write_bitmap(
        string_env_icon.bitmap,
        string_env_icon.pixel_shader,
        filename="string_env_icon.bmp",
        overwrite=True,
    )
    w_store.write_bitmap(
        chime_steel_env_icon.bitmap,
        chime_steel_env_icon.pixel_shader,
        filename="chime_steel_env_icon.bmp",
        overwrite=True,
    )
    print(" completed")

# Test 12: Write filter object to a file
if 12 in TEST_LIST:
    pass

# Test 13: Read filter object from file
if 13 in TEST_LIST:
    pass

# Test 14: Display wave table bitmap with transparency
if 14 in TEST_LIST:
    print("\nTest 14: Display wave table bitmap with transparency")
    new_bitmap = w_store.read_bitmap("streetchicken.bmp")
    splash.append(
        displayio.TileGrid(
            new_bitmap.bitmap, pixel_shader=new_bitmap.pixel_shader, x=170, y=15
        )
    )
print(" completed")

# All tests completed
print("\n*** All tests completed ***")
# pylint: disable=no-member
print(f"mem_free delta: {gc.mem_free() - m0}")
print(f"time delta: {time.monotonic() - t0}")
while True:
    pass
