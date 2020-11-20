import wifi
import munin
wifi.connect()
n = munin.Node();

# Slow down the processor, full speed is not really needed.
import machine
machine.freq(80000000)
# set the CPU frequency to 80 MHz, minimum for wifi to work !

while True:
    n.start()
