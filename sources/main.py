import wifi
import munin
wifi.connect()
n = munin.Node();
while True:
    n.start()
