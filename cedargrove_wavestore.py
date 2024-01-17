# SPDX-FileCopyrightText: Copyright (c) 2024 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
"""
`cedargrove_wavestore`
================================================================================

A CircuitPython class to create and manage a file-based collection of synthio
file assets.

* Author(s): JG

Implementation Notes
--------------------

**Software and Dependencies:**
* ulab for CircuitPython
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import os
import displayio
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

    # #pylint#: disable=too-many-arguments
    def __init__(self, spi_pins, cs_pin, debug=True):
        # board.SPI(), board.D20 for the UM FeatherS2

        self._spi_pins = spi_pins
        self._cs_pin = cs_pin
        self._debug = debug

        self.printd("WaveStore class: initializing...")

        # Initialize and mount the SD card
        sd_card = sdcardio.SDCard(self._spi_pins, self._cs_pin)
        self._vfs = storage.VfsFat(sd_card)
        storage.mount(self._vfs, "/sd")

        self.printd("WaveStore init: SD card mounted")

    def write_screen(self, display, filename="screenshot.bmp", overwrite=False):
        """Write the screen contents to a .bmp file.
        :param displayioi.display display: The display object. No default.
        :param str filename: The target filename and extension. The file will be
        written to the root directory of the SD card. No default.
        :param bool overwrite: Overwrite the file. Defaults to False; do not overwrite.
        """
        self.printd(f"write_screen_to_file: writing /sd/{filename}")
        if filename not in self.get_catalog() or overwrite:
            save_pixels(f"/sd/{filename}", display)
            self.printd(f"write_screen_to_file: /sd/{filename} saved")
        else:
            self.printd(f"write_screen_to_file: /sd/{filename} NOT saved")

    def write_bitmap(self, bitmap, palette, filename="bitmap.bmp", overwrite=False):
        """Write a bitmap image to a .bmp file.
        :param bitmap bitmap: The bitmap object. No default.
        :param displayio.Palette palette: The bitmap palette object. No default.
        :param str filename: The target filename and extension. The file will
        be written to the root directory of the SD card. No default.
        :param bool overwrite: Overwrite the file. Defaults to False; do not
        overwrite.
        """
        self.printd(f"write_bitmap_to_file: writing /sd/{filename}")
        if filename not in self.get_catalog() or overwrite:
            save_pixels(f"/sd/{filename}", bitmap, palette)
            self.printd(f"write_bitmap_to_file: /sd/{filename} saved")
        else:
            self.printd(f"write_bitmap_to_file: /sd/{filename} NOT saved")

    def read_bitmap(self, filename="bitmap.bmp"):
        """Read a .bmp file and return the bitmap as a TileGrid object to be
        added to a displayio.Group object.
        :param str filename: The target filename and extension. No default."""
        self.printd(f"read_bitmap_from_file: /sd/{filename}")
        image = displayio.OnDiskBitmap(f"/sd/{filename}")
        return displayio.TileGrid(image, pixel_shader=image.pixel_shader)

    def read_wavetable(self, filename):
        """Reads wave file and returns a memoryview object.
        :param str filename: The filename and extension. No default."""
        self.printd(f"read_waveform: /sd/{filename}")
        with adafruit_wave.open(f"/sd/{filename}") as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform: unsupported format")
            return memoryview(w.readframes(w.getnframes())).cast("h")

    def read_wavetable_ulab(self, filename):
        """Reads wave file and returns a ulab.numpy array object. Allows it to
        be lerp()-ed to mix with another wave. Usage:
        my_wave = read_waveform_ulab("AKWF_0001.wav")
        :param str filename: The filename and extension. No default."""
        self.printd(f"read_waveform_ulab: /sd/{filename} ")
        with adafruit_wave.open(f"/sd/{filename}") as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform_ulab: unsupported format")
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)

    def write_wavetable(self, wave_table, filename, overwrite=False):
        """Formats and writes wave_table into a standard .wav file.
        :param ReadableBuffer wave_table: The wave_table object. No default.
        :param str filename: The target filename and extension. The file will be
        written to the root directory of the SD card. No default.
        :param bool overwrite: Overwrite the file. Defaults to False; do not
        overwrite.
        """
        self.printd(f"write_wave_to_file: writing /sd/{filename}")
        if filename not in self.get_catalog() or overwrite:
            with adafruit_wave.open(f"/sd/{filename}", mode="w") as w:
                pass
            self.printd(f"write_wave_to file: /sd/{filename} saved")
        else:
            self.printd(f"write_wave_to_file: /sd/{filename} NOT saved")
        self.printd(f"{wave_table} {w}")

    def get_catalog(self, path="/sd"):
        """Looks at the SD card file system and returns a list of files in the
        root directory.
        :param str path: The directory path. Defaults to the SD card root
        directory."""
        self.printd(f"get_catalog: retrieving {path} file list")
        catalog = [
            file
            for file in os.listdir(path)
            if not (os.stat(path + "/" + file)[0] & 0x4000)
        ]
        return catalog

    def printd(self, string):
        """Print string contents if debug is True.
        :param str string: The string to be printed."""
        if self._debug:
            print(string)
