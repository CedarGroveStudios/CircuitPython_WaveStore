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
import synthio
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

        self.printd("WaveStore class: initializing...")

        # Initialize and mount the SD card
        sd_card = sdcardio.SDCard(self._spi_pins, self._cs_pin)
        self._vfs = storage.VfsFat(sd_card)
        storage.mount(self._vfs, "/sd")

        self.printd("WaveStore init: SD card mounted")

    def write_screen(self, display, filename, path="/sd", overwrite=False):
        """Write the screen contents to a .bmp file.
        :param displayioi.display display: The display object. No default.
        :param str filename: The target filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory.
        :param bool overwrite: Overwrite the file. Defaults to False; do not overwrite.
        """
        self.printd(f"write_screen: writing {path}/{filename}")
        if filename in self.get_catalog(path) and not overwrite:
            self.printd(f"write_screen: {path}/{filename} NOT saved")
        else:
            save_pixels(f"/sd/{filename}", display)
            self.printd(f"write_screen_to_file: {path}/{filename} saved")

    def read_bitmap(self, filename, path="/sd"):
        """Read a .bmp file and return the bitmap as a TileGrid object to be
        added to a displayio.Group object.
        :param str filename: The target filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory."""
        self.printd(f"read_bitmap_from_file: {path}/{filename}")
        image = displayio.OnDiskBitmap(f"{path}/{filename}")
        return displayio.TileGrid(image, pixel_shader=image.pixel_shader)

    def write_bitmap(self, bitmap, palette, filename, path="/sd", overwrite=False):
        """Write a bitmap image to a .bmp file.
        :param bitmap bitmap: The bitmap object. No default.
        :param displayio.Palette palette: The bitmap palette object. No default.
        :param str filename: The target filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory.
        :param bool overwrite: Overwrite the file. Defaults to False; do not
        overwrite.
        """
        self.printd(f"write_bitmap: writing {path}/{filename}")

        if filename in self.get_catalog(path) and not overwrite:
            self.printd(f"write_bitmap: {path}/{filename} NOT saved")
        else:
            save_pixels(f"{path}/{filename}", bitmap, palette)
            self.printd(f"write_bitmap: {path}/{filename} saved")

    def read_envelope(self, filename, path="/sd"):
        """Reads envelope file and returns a synthio.Envelope object.
        :param str filename: The filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory."""
        self.printd(f"read_envelope: {path}/{filename}")
        with open(f"{path}/{filename}", mode="r") as r:
            params = r.read()
            # pylint: disable=eval-used
            params = eval(params)
            new_env = synthio.Envelope(
                attack_time=params[0],
                decay_time=params[1],
                release_time=params[2],
                attack_level=params[3],
                sustain_level=params[4],
            )
            self.printd(f"read_envelope: {new_env}")
            return new_env

    def write_envelope(self, envelope, filename, path="/sd", overwrite=False):
        """Writes synthio.Envelope object into a text file.
        :param synthio.Envelope envelope: The envelope object. No default.
        :param str filename: The target filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory.
        :param bool overwrite: Overwrite the file. Defaults to False; do not
        overwrite.
        """
        self.printd(f"write_envelope: writing {path}/{filename}")
        if filename in self.get_catalog(path) and not overwrite:
            self.printd(f"write_envelope: {path}/{filename} NOT written")
        else:
            params = str(list(envelope)) + "\n"
            with open(f"{path}/{filename}", mode="w") as w:
                w.write(params)
                self.printd(f"write_envelope: {path}/{filename} written")
                self.printd(f"write_envelope: {envelope}")

    def read_wavetable(self, filename, path="/sd"):
        """Reads wave file and returns a memoryview object.
        :param str filename: The filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory."""
        self.printd(f"read_wavetable: {path}/{filename}")
        with adafruit_wave.open(f"{path}/{filename}") as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform: unsupported format")
            return memoryview(w.readframes(w.getnframes())).cast("h")

    def read_wavetable_ulab(self, filename, path="/sd"):
        """Reads wave file and returns a ulab.numpy array object. Allows it to
        be lerp()-ed to mix with another wave. Usage:
        my_wave = read_waveform_ulab("AKWF_0001.wav")
        :param str filename: The filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory."""
        self.printd(f"read_waveform_ulab: {path}/{filename} ")
        with adafruit_wave.open(f"{path}/{filename}") as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("read_waveform_ulab: unsupported format")
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)

    def write_wavetable(
        self, wave_table, filename, path="/sd", samp_rate=22050, overwrite=False
    ):
        """Formats and writes wave_table into a standard .wav file.
        :param ReadableBuffer wave_table: The wave_table object. No default.
        :param str filename: The target filename and extension. No default.
        :param str path: The directory path. Defaults to the SD card root
        directory.
        :param int samp_rate: The sample rate (same as frame rate) for the wave
        table file. Defaults to 22050 samples per second.
        :param bool overwrite: Overwrite the file. Defaults to False; do not
        overwrite.
        """
        self.printd(f"write_wavetable: writing {path}/{filename}")
        if filename in self.get_catalog(path) and not overwrite:
            self.printd(f"write_wavetable: {path}/{filename} NOT written")
        else:
            with adafruit_wave.open(f"{path}/{filename}", mode="w") as w_table:
                w_table.setnchannels(1)
                w_table.setsampwidth(2)  # each sample is two bytes
                w_table.setframerate(samp_rate)
                w_table.writeframes(wave_table)
            self.printd(f"write_wavetable: {path}/{filename} written")

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
            print(f"   WaveStore: {string}")
