import wifi
from machine import I2C, Pin
import munin
wifi.connect()

i2c = I2C(0, scl=Pin(22), sda=Pin(21));
n = munin.Node(i2c=i2c);

# Slow down the processor, full speed is not really needed.
import machine
machine.freq(80000000)
# set the CPU frequency to 80 MHz, minimum for wifi to work !

while True:
    n.start()
