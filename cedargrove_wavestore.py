# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`cedargrove_wavestore`
================================================================================

A CircuitPython class to create and manage a collection of synthio wave_tables.


* Author(s): JG

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**
* ulab for CircuitPython
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import sdcardio
import storage
import ulab.numpy as np
import adafruit_wave
from adafruit_bitmapsaver import save_pixels

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_WaveStore.git"


class WaveStore:
    """
    The WaveStore class ...

    :param pin spi_pins: The ... No default.
    :param pin cs_pin: The ... No default.
    :param bool debug: The ... Defaults to False (do not print debug statements).
    """

    # pylint: disable=too-many-arguments
    def __init__(self, spi_pins, cs_pin, debug=True):
        # board.SPI(), board.D20 for the UM FeatherS2

        self._spi_pins = spi_pins
        self._cs_pin = cs_pin
        self._debug = debug

        sd_card = sdcardio.SDCard(self._spi_pins, self._cs_pin)
        vfs = storage.VfsFat(sd_card)
        storage.mount(vfs, "/sd")

    def capture_screen_to_file(self, display, filename="screenshot"):
        self.printd(f"/sd/{filename}.bmp : Taking Screenshot...")
        save_pixels("/sd/" + filename + ".bmp", display)
        print('... Screenshot Taken')

    def capture_bitmap_to_file(self, bitmap, filename="screenshot"):
        self.printd(f"/sd/{filename}.bmp : Taking Screenshot...")
        save_pixels("/sd/" + filename + ".bmp", bitmap)
        print('... Screenshot Taken')

    def read_waveform(self, filename):
        """Reads entire wave file."""
        self.printd(f"/sd/{filename} : Reading Waveform...")
        with adafruit_wave.open(f"/sd/{filename}.wav") as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform: unsupported format")
            return memoryview(w.readframes(w.getnframes())).cast('h')

    def read_waveform_ulab(self, filename):
        """Read wave file and make it lerp()-able to mix with another wave."""
        self.printd(f"/sd/{filename} : Reading Waveform (ulab) ...")
        with adafruit_wave.open(f"/sd/{filename}.wav") as w:
            if w.getsampwidth() != 2 or w.getchannels() != 1:
                raise ValueError("read_waveform_ulab: unsupported format")
            return np.frombuffer(w.readframs(w.getnframes()), dtype=np.int16)

    # usage example
    # my_wave = read_waveform("AKWF_granular_0001.wav")

    def write_waveform(self, wave_table, filename):
        """Formats and writes wave_table into a standard .wav file."""
        self.printd(f"/sd/{filename} : Writing Waveform...")
        with adafruit_wave.open(f"/sd/{filename}.wav", "W") as w:
            pass

    def get_catalog(self):
        """Looks at the SD card file system and returns a list of .wav files
        and a list of .bmp files."""
        self.printd("Reading Catalog...")

    def printd(self, string):
        if self._debug:
            print(string)
