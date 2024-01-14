# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
"""
`cedargrove_wavestore`
================================================================================

A CircuitPython class to create and manage a file-based collection of synthio
wave_tables.

* Author(s): JG

Implementation Notes
--------------------

**Software and Dependencies:**
* ulab for CircuitPython
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import displayio
import os
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

        self.printd("WaveStore class initializing...")

        sd_card = sdcardio.SDCard(self._spi_pins, self._cs_pin)
        self._vfs = storage.VfsFat(sd_card)
        storage.mount(self._vfs, "/sd")

        self.printd("WaveStore init: SD card mounted")

    def write_screen_to_file(self, display, filename="screenshot.bmp"):
        """Write the screen contents to a .bmp file."""
        filename = f"/sd/{filename}"
        self.printd(f"write_screen_to_file: {filename}")
        save_pixels(filename, display)
        print("... Screenshot Stored")

    def write_bitmap_to_file(self, bitmap, filename="bitmap.bmp"):
        """Write a bitmap image to a .bmp file."""
        filename = f"/sd/{filename}"
        self.printd(f"write_bitmap_to_file: {filename}")
        save_pixels(filename, bitmap)
        print("... Bitmap Stored")

    def read_bitmap_from_file(self, filename="bitmap.bmp"):
        """Read a .bmp file and return the bitmap as a TileGrid object."""
        filename = f"/sd/{filename}"
        self.printd(f"read_bitmap_from_file: {filename}")
        image = displayio.OnDiskBitmap(filename)

        # Create a TileGrid to hold the bitmap and return
        # to be appended to a displayio.Group object
        return displayio.TileGrid(image, pixel_shader=image.pixel_shader)

    def read_waveform(self, filename):
        """Reads entire wave file."""
        filename = f"/sd/{filename}"
        self.printd(f"read_waveform: {filename} ")
        with adafruit_wave.open(filename) as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform: unsupported format")
            return memoryview(w.readframes(w.getnframes())).cast("h")

    def read_waveform_ulab(self, filename):
        """Read wave file and make it lerp()-able to mix with another wave.
        Usage example: my_wave = read_waveform_ulab("AKWF_0001.wav")"""
        filename = f"/sd/{filename}"
        self.printd(f"read_waveform_ulab: {filename} ")
        with adafruit_wave.open(filename) as w:
            if w.getsampwidth() != 2 or w.getchannels() != 1:
                raise ValueError("read_waveform_ulab: unsupported format")
            return np.frombuffer(w.readframs(w.getnframes()), dtype=np.int16)

    def write_waveform(self, wave_table, filename):
        """Formats and writes wave_table into a standard .wav file."""
        filename = f"/sd/{filename}"
        self.printd(f"write_waveform: {filename} ")
        with adafruit_wave.open(f"/sd/{filename}", mode="w") as w:
            pass

    def get_catalog(self, path="/sd"):
        """Looks at the SD card file system and returns a list of files in the root directory."""
        self.printd(f"get_catalog: retrieving file list")
        catalog = [
            file
            for file in os.listdir(path)
            if not (os.stat(path + "/" + file)[0] & 0x4000)
        ]
        return catalog

    def printd(self, string):
        """Print string contents if debug is True."""
        if self._debug:
            print(string)
