# E-ink display: GDEH0213B73 v2.0
# Controler: SSD1675B

import epaper2in13
from machine import Pin, SPI
# import framebuf
import font
mosi = Pin(23, Pin.OUT)
miso = Pin(34, Pin.IN)
sck = Pin(18, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(16, Pin.OUT)
busy = Pin(4, Pin.IN)
dc = Pin(17, Pin.OUT)

spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)
e = epaper2in13.EPD(spi, cs, dc, rst, busy)
e.init()

w = 128
h = 250
x = 0
y = 0

buf = bytearray(w * h // 8)
# fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
black = 0
white = 255

for i in range(len(buf)):
    buf[i] = white

e.set_frame_memory(buf, x, y, w, h)
e.display_frame()

font.write(buf, 1, "Bonjour".center(17))
font.write(buf, 3, "tout".center(17))
font.write(buf, 5, "le monde".center(17))
e.set_frame_memory(buf, 0, 0, w, h)
e.display_frame()
