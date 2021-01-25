"""
MicroPython Waveshare 2.13" Black/White GDEH0213B1 e-paper display driver
https://github.com/mcauser/micropython-waveshare-epaper

MIT License
Copyright (c) 2017 Waveshare
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from time import sleep_ms
import ustruct

# Display resolution
EPD_WIDTH = const(128)
EPD_HEIGHT = const(250)
# datasheet says 250x122 (increased to 128 to be multiples of 8)

# Display commands
DRIVER_OUTPUT_CONTROL = const(0x01)
# Gate Driving Voltage Control       0x03
# Source Driving voltage Control     0x04
BOOSTER_SOFT_START_CONTROL = const(0x0C)  # not in datasheet
# GATE_SCAN_START_POSITION             = const(0x0F) # not in datasheet
DEEP_SLEEP_MODE = const(0x10)
DATA_ENTRY_MODE_SETTING = const(0x11)
# SW_RESET                             = const(0x12)
# TEMPERATURE_SENSOR_CONTROL           = const(0x1A)
MASTER_ACTIVATION = const(0x20)
# DISPLAY_UPDATE_CONTROL_1             = const(0x21)
DISPLAY_UPDATE_CONTROL_2 = const(0x22)
# Panel Break Detection              0x23
WRITE_RAM = const(0x24)
WRITE_VCOM_REGISTER = const(0x2C)
# Status Bit Read                    0x2F
WRITE_LUT_REGISTER = const(0x32)
SET_DUMMY_LINE_PERIOD = const(0x3A)
SET_GATE_TIME = const(0x3B)
# BORDER_WAVEFORM_CONTROL              = const(0x3C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER = const(0x4F)
TERMINATE_FRAME_READ_WRITE = const(0xFF)  # not in datasheet, aka NOOP

BUSY = const(1)  # 1=busy, 0=idle


class EPD:

    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

#    LUT_FULL_UPDATE    = bytearray(b'\x22\x55\xAA\x55\xAA\x55\xAA\x11\x00\x00\x00\x00\x00\x00\x00\x00\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x01\x00\x00\x00\x00\x00')
#    LUT_PARTIAL_UPDATE = bytearray(b'\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    # FULL_UPDATE_LUT_TTGO_B73 --> 100 bytes
    LUT_FULL_UPDATE = bytearray(b'\xa0\x90P\x00\x00\x00\x00\x00\x00\x00P\x90\xa0\x00\x00\x00\x00\x00\x00\x00\xa0\x90P\x00\x00\x00\x00\x00\x00\x00P\x90\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x0f\x00\x00\x00\x0f\x0f\x00\x00\x03\x0f\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    LUT_PARTIAL_UPDATE = bytearray(b'@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()
        self._command(DRIVER_OUTPUT_CONTROL)
        self._data(bytearray([(EPD_HEIGHT - 1) & 0xFF]))
        self._data(bytearray([((EPD_HEIGHT - 1) >> 8) & 0xFF]))
        self._data(bytearray([0x00]))  # GD = 0 SM = 0 TB = 0
        self._command(BOOSTER_SOFT_START_CONTROL, b'\xD7\xD6\x9D')
        self._command(WRITE_VCOM_REGISTER, b'\xA8')  # VCOM 7C
        self._command(SET_DUMMY_LINE_PERIOD, b'\x1A')  # 4 dummy lines per gate
        self._command(SET_GATE_TIME, b'\x08')  # 2us per line
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')  # X increment Y increment
        self.set_lut(self.LUT_FULL_UPDATE)

    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(200)

    def set_lut(self, lut):
        self._command(WRITE_LUT_REGISTER, lut)

    # put an image in the frame memory
    def set_frame_memory(self, image, x, y, w, h):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x = x & 0xF8
        w = w & 0xF8

        if (x + w >= self.width):
            x_end = self.width - 1
        else:
            x_end = x + w - 1

        if (y + h >= self.height):
            y_end = self.height - 1
        else:
            y_end = y + h - 1

        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        self._command(WRITE_RAM, image)

    # replace the frame memory with the specified color
    def clear_frame_memory(self, color):
        self.set_memory_area(0, 0, self.width - 1, self.height - 1)
        self.set_memory_pointer(0, 0)
        self._command(WRITE_RAM)
        # send the color data
        for i in range(0, self.width // 8 * self.height):
            self._data(bytearray([color]))

    # draw the current frame memory and switch to the next memory area
    def display_frame(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xC4')
        self._command(MASTER_ACTIVATION)
        self._command(TERMINATE_FRAME_READ_WRITE)
        self.wait_until_idle()

    # specify the memory area for data R/W
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._data(bytearray([(x_start >> 3) & 0xFF]))
        self._data(bytearray([(x_end >> 3) & 0xFF]))
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION, ustruct.pack("<HH", y_start, y_end))

    # specify the start point for data R/W
    def set_memory_pointer(self, x, y):
        self._command(SET_RAM_X_ADDRESS_COUNTER)
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._data(bytearray([(x >> 3) & 0xFF]))
        self._command(SET_RAM_Y_ADDRESS_COUNTER, ustruct.pack("<H", y))
        self.wait_until_idle()

    # to wake call reset() or init()
    def sleep(self):
        self._command(DEEP_SLEEP_MODE)
        self.wait_until_idle()
