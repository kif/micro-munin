import wifi
import munin
wifi.connect()
n = munin.Node();

# Slow down the processor, full speed is not really needed.
import machine
machine.freq(40000000)  # set the CPU frequency to 40 MHz

while True:
    n.start()
