import epaper2in13
from machine import Pin, SPI

mosi = Pin(23, Pin.OUT)
miso = Pin(34, Pin.IN)
sck = Pin(18, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(16, Pin.OUT)
busy = Pin(4, Pin.IN)
dc = Pin(17, Pin.OUT)

spi = SPI(2, baudrate=4000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)
e = epaper2in13.EPD(spi, cs, dc, rst, busy)
e.init()

w = 128
h = 250
x = 0
y = 0

import framebuf
buf = bytearray(w * h // 8)
fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
black = 0
white = 1
fb.fill(white)
