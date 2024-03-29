Introduction
============

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/CedarGroveStudios/CircuitPython_WaveStore/workflows/Build%20CI/badge.svg
    :target: https://github.com/CedarGroveStudios/CircuitPython_WaveStore/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A CircuitPython class to create and manage a collection of synthio object file assets.


Dependencies
=============
This library depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.



Usage Example
=============

.. code-block:: python

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
    if 1 in TEST_LIST:
        # Test 1: Get the SD directory and print list to REPL
        print("\nTest 1: Get the SD directory and print list to REPL")
        print(f"SD directory: {w_store.get_catalog()}")
        print(" completed")

    if 2 in TEST_LIST:
        # Test 2: Write waveform bitmap images to files
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

    if 3 in TEST_LIST:
        # Test 3: Read and display saved bitmap
        print("\nTest 3: Read and display saved bitmap")
        new_bitmap = w_store.read_bitmap("harp_icon.bmp")
        new_bitmap.x = 10
        new_bitmap.y = 10
        splash.append(new_bitmap)
        print(" completed")

    if 4 in TEST_LIST:
        # Test 4: Add second icon and envelopes; save entire screen to a file
        print("\nTest 4: Add second icon and envelopes; save entire screen to a file")
        splash.append(chime_icon)
        splash.append(string_env_icon)
        splash.append(chime_steel_env_icon)
        w_store.write_screen(display, "screenshot.bmp", overwrite=True)
        print(" completed")

    if 5 in TEST_LIST:
        # Test 5: Clear the screen and read and display saved screenshot
        print("\nTest 5: Clear the screen and read and display saved screenshot")
        splash.pop()
        splash.pop()
        time.sleep(1)  # Wait for a moment to show blank screen
        splash.append(w_store.read_bitmap("screenshot.bmp"))
        print(" completed")

    if 6 in TEST_LIST:
        # Test 6: Write wave tables to files
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

    if 7 in TEST_LIST:
        # Test 7: Read wavetable as memory_view object from a file and display
        print("\nTest 7: Read wavetable as memory_view object from a file and display")
        wave_table = w_store.read_wavetable("harp.wav")
        print(f"w_store.read_wavetable: {wave_table}")
        harp_icon.wave_table = w_store.read_wavetable("harp.wav")
        print(" completed")

    if 8 in TEST_LIST:
        # Test 8: Read wave table as ulab array from a file and display
        pass

    if 9 in TEST_LIST:
        # Test 9: Write envelope objects to files
        print("\nTest 9: Write envelope objects to files")
        w_store.write_envelope(string_envelope, "string.env", overwrite=True)
        w_store.write_envelope(chime_steel_envelope, "chime_steel.env", overwrite=True)
        print(" completed")

    if 10 in TEST_LIST:
        # Test 10: Read envelope object from a file
        print("\nTest 10: Read envelope object from a file")
        new_env = w_store.read_envelope("string.env")
        print(" completed")

    if 11 in TEST_LIST:
        # Test 11: Write envelope bitmap image to a file
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

    if 12 in TEST_LIST:
        # Test 12: Write filter object to a file
        pass

    if 13 in TEST_LIST:
        # Test 13: Read filter object from file
        pass

    if 14 in TEST_LIST:
        # Test 14: Display wave table bitmap with transparency
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



Documentation
=============



Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_WaveStore/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
