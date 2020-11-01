# Micro-Munin

Munin node+plugins written for micropython

## Idea: 

Use `munin` to collect for domotic purposes: collect data and generates graphs

## Hardware

* ESP32 microcontroler boards are suitable for running micropython and provides many programmable pins to read sensors and connect to the wifi or bluetooth.
* DHT22 temperature and humidity sensor
* ESP32 features a magnetic sensor (Hall effect) 

## Software

In addition to micropython, this is a server which opens the port 4949 and accepts connection. 
The protocole for munin is fairly simple ...

 - config
 - fetch

The most difficult was to implement the munin protocol properly 

The code requires in addition a `_secret.py` file containing local information not to be shared like:
```
name = 'name-of-the-device'
essid = "Name of wifi network"
password = "Wifi password"
ip = "192.168.0.1"
subnet = '255.255.255.0'
gateway = '192.168.0.254'
dns = '8.8.8.8'
pin = 22  # Where the DHT22 is connected
```

## Enclosure

As I used this development board which features a battery connector, the device is automomous (for several hours):

https://fr.aliexpress.com/item/32819459737.html
https://www.amazon.fr/Bluetooth-Battery-ESP-32S-d%C3%A9veloppement-battery/dp/B083JRTSQ2

The drawback is that the enclosure is much larger for the battery.

The 3D model, generated with FreeCAD, is in the CAD folder. AMF files can directly be sliced and printed with Slic3r. 

## Bill:

* ESP32 development board: ~10€
* DHT22 sensor ~2€
* Battery 10€
* 3D printed encosure: 1€