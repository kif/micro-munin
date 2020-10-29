import network
from _secret import essid, password, ip, subnet, gateway, dns


def connect():
    "Connect to the wifi"

    station = network.WLAN(network.STA_IF)

    if station.isconnected() == True:
        print("Already connected")
        return

    station.active(True)
    station.connect(essid, password)
    station.ifconfig((ip, subnet, gateway, dns))

    while station.isconnected() == False:
        pass

    print("Connection successful")
    print(station.ifconfig())


def disconnect():
    station = network.WLAN(network.STA_IF)
    station.disconnect()
    station.active(False)
