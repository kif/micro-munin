# Micro-Munin

Munin node+plugins written for micropython

## Idea: 

Use munin as data broker for domotic purposes and use it to generates graphs

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

## Enclosure

The last thing to do: 3D printed case !
