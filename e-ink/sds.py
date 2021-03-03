try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from micropython import const
except ImportError:
    const = lambda x: x

from collections import namedtuple
Dust = namedtuple("Dust", ["PM2_5", "PM10"])

# uart_sds = UART(2, tx=12, rx=27)
# uart_sds.init(9600, 8, None)
# sreader_sds = asyncio.StreamReader(uart_sds)  # Create a StreamReader


# port=1, baud=9600
class SDS:
    "A class receiving particule measurement from SDS sensor"

    def __init__(self, sreader, callback=None, read_delay=1):
        """
        :param sreader: async UART reader
        :param callback: to be called every update
        """
        self._sreader = sreader
        self._callback = callback
        self.last_value = None
        asyncio.create_task(self._run(read_delay))

    def __repr__(self):
        return "SDS sensor at {}".format(self.get())

    def __iter__(self):  # Await 1st reading
        while self.last_value is None:
            yield from asyncio.sleep(0)

    ##########################################
    # Data Stream Handler Functions
    ##########################################

    async def _run(self, read_delay):
        while True:
            res = await self._sreader.read(128)
            self._update(res)
            await asyncio.sleep(read_delay)  # Ensure task runs and res is copied

    def _update(self, datagram):
        l = len(datagram)
        i = 0
        while i + 9 < l:
            b = datagram[i]
            c = datagram[i + 1]
            e = datagram[i + 9]
            if (b == 170) and (c == 192) and (e == 171):
                # likely a datagram
                data1, data2, data3, data4, data5, data6 = datagram[i + 2:i + 8]
                if (data1 + data2 + data3 + data4 + data5 + data6) % 256 == datagram[i + 8]:
                    # Yes it is a valid datagram
                    self.last_value = Dust((data1 + data2 * 256) / 10.0,
                                           (data3 + data4 * 256) / 10.0)
                    if callable(self._callback):
                        self._callback(self.last_value)
                    i += 10
                else:
                    i += 1

    def get(self, what=None):
        if what == "header":
            return " PM2.5   PM10"
        elif what == "unit":
            return "Dust", ["PM2.5 (µg/m³)", "PM10 (µg/m³)"]
        elif what == "text":
            value = self.last_value
            if value:
                return "{:6.1f} {:6.1f}".format(value[0], value[1])
            else:
                return "  None   None"
        else:
            return self.last_value
