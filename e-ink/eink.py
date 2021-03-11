# E-ink display: GDEH0213B73 v2.0
# Controler: SSD1675B
import uasyncio as asyncio
import epaper2in13
from machine import Pin, SPI, I2C, UART
import time
from htu21d import HTU21D
from sds import SDS

print("Initialize HTU")
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
htu = HTU21D(i2c)

print("Initialize eink")
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

e.print("Sensor-S", align="center", update=False)
# e.display_frame()

uart_sds = UART(2, tx=12, rx=27)
uart_sds.init(9600, 8, None)
sreader_sds = asyncio.StreamReader(uart_sds)  # Create a StreamReader
sds = SDS(sreader_sds)  # Instantiate SDS


async def main():
    await htu
    await sds
#     fstr_htu = 'T:{:4.1f}C RH:{:4.1f}%'
#     fstr_sds = 'PM2.5{:4.1f} PM10{:4.1f}'
    while True:
#         print(fstr_htu.format(htu.temperature, htu.humidity) + " " + fstr_sds.format(*sds.last_value))
        e.print("Temp: {:5.2f} deg C".format(htu.temperature), where=1, update=False)
        e.print("Hum : {:5.2f} % rel".format(htu.humidity), where=2, update=False)
        e.print("PM2.5 {:5.1f} ug/m3".format(sds.last_value.PM2_5), where=3, update=False)
        e.print("PM10: {:5.1f} ug/m3".format(sds.last_value.PM10), where=4, update=True)
        await asyncio.sleep(2)


print("Start loop")
asyncio.run(main())
