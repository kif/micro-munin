import dht
import machine
import esp32
import network
from _secret import pin, name, essid
import socket
import select
import time
b_essid = essid.encode()
station = network.WLAN(network.STA_IF)


class Node:
    error = b'# Unknown service\n.\n'
    expose = {b"meteo_temperature": b"graph_title DHT22 temperature\n"
                                    b'graph_vlabel degrees Celsius\n'
                                    b'graph_category sensors\n'
                                    b'graph_info This graph shows the temperature sensor of DHT22\n'
                                    b'dht22.info Temperature\n'
                                    b'dht22.min 0\n'
                                    b'dht22.max 70\n'
                                    b'dht22.label Temperature inside\n'
                                    b'esp32.info Temperature\n'
                                    b'esp32.min 0\n'
                                    b'esp32.max 70\n'
                                    b'esp32.label Temperature of the chip\n'
                                    b'.\n',
              b"magnetic": b"graph_title Hall effect sensor\n"
                                    b'graph_vlabel Magnetic field\n'
                                    b'graph_category sensors\n'
                                    b'graph_info This graph shows the magnetic field on the ESP32\n'
                                    b'esp32.info Magnetic\n'
                                    b'esp32.min -1024\n'
                                    b'esp32.max 1024\n'
                                    b'esp32.label Magnetic field\n'
                                    b'.\n',
              b"meteo_humidity": b'graph_title DHT22 humidity sensor\n'
                                   b'graph_vlabel % Relative humidity\n'
                                   b'graph_category sensors\n'
                                   b'graph_info This graph shows the relative humidity sensor of the DHT22\n'
                                   b'dht22.info Relative humidity\n'
                                   b'dht22.min 0\n'
                                   b'dht22.max 100\n'
                                   b'dht22.label Humidity inside\n'
                                   b'.\n',
              b"cpuspeed": b'graph_title CPU frequency scaling\n'
                            b'graph_args --base 1000\n'
                            b'graph_category system\n'
                            b'graph_vlabel Hz\n'
                            b'graph_info This graph shows the average running speed of each CPU.\n'
                            b'cpu0.cdef cpu0,1000,*\n'
                            b'cpu0.label CPU 0\n'
                            b'cpu0.max 300000000\n'
                            b'cpu0.min 80000000\n'
                            b'cpu0.type DERIVE\n'
                            b'.\n',
              b"wifi": b"graph_title Strength of the wifi signal\n"
                       b'graph_vlabel Wifi signal\n'
                       b'graph_category network\n'
                       b'graph_info This graph shows the strength of the WiFi signal\n'
                       b'esp32.info Wifi\n'
                       b'esp32.min -1024\n'
                       b'esp32.max 1024\n'
                       b'esp32.label Magnetic field\n'
                       b'.\n',
              }

    def __init__(self, port=4949, name=name, pin=pin):
        self.last_read = 0  # utime.ticks_ms()
        self.dht = dht.DHT22(machine.Pin(pin))
        self.name = name
        self.addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        print("Munin node %s bound to %s" % (self.name, self.addr))
        self.server_socket = None
        self.clients = []

    def _read(self):
        now = time.ticks_ms()
        # TODO: check the dtype of time.ticks_ms()
        if abs(time.ticks_diff(now, self.last_read)) > 2048:
            self.dht.measure()
            self.last_read = now
        return self.dht

    def get_list(self):
        return b" ".join(list(self.expose.keys()))

    def get_config(self, what):
        return self.expose.get(what, self.error)

    def fetch(self, what):
        if what == b"meteo_temperature":
            tesp = (esp32.raw_temperature() - 32) * 5 / 9
            tdht = self._read().temperature()
            return b'esp32.value %.2f\ndht22.value %.2f\n.\n' % (tesp, tdht)
        elif what == b"meteo_humidity":
            return b'dht22.value %.2f\n.\n' % self._read().humidity()
        elif what == b'cpuspeed':
            return b'cpu0.value %d\n.\n' % machine.freq()
        elif what == b'magnetic':
            return b'esp32.value %d\n.\n' % esp32.hall_sensor()
        elif what == b'wifi':
            lst = [ i[3] for i in station.scan() if i[0] == b_essid]
            if lst:
                return b'wifi.value %d\n.\n' % lst[0]
            else:
                return b'wifi.value 0\n.\n'
        else:
            return self.error

    def start(self):
        # Start the server
        self.flush()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(self.addr)
        self.server_socket.listen(5)

        while True:
            requested_conn, wlist, xlist = select.select([self.server_socket], [], [], 0.1)
            # print(requested_conn, wlist, xlist)
            for connexion in requested_conn:
                client, remote_addr = connexion.accept()
                if client not in self.clients:
                    # bienvenu
                    print('Client connected from', remote_addr)
                    self.clients.append(client)
                    client.send(b"# munin node at %s \n" % self.name)

            try:
                to_read, wlist, xlist = select.select(self.clients, [], [], 0.1)
            except select.error:
                to_read = []
#             else:
#                 print(to_read, wlist, xlist)
            for client in to_read:
                try:
                    line = client.recv(2048).strip()
#                     print("<<<", line)
                    if line in (b'.', b"quit"):
                        self.clients.remove(client)
                        client.close()
                    elif line.startswith(b"cap"):
                        client.send(b'cap multigraph dirtyconfig\n')
                    elif line.startswith(b"list"):
                        client.send(self.get_list() + b'\n')
                    elif line == b"nodes":
                        client.send(b'%s\n.\n' % self.name)
                    elif line.startswith(b"config"):
                        requested = line.split()
                        if len(requested) == 1:
                            client.send(self.error)
                        else:
                            for what in requested[1:]:
                                client.send(self.get_config(what))
                    elif line.startswith(b"fetch"):
                        requested = line.split()
                        if len(requested) == 1:
                            client.send(self.error)
                        else:
                            for what in requested[1:]:
                                client.send(self.fetch(what))

                    elif line == b"version":
                        client.send(b'munins node on %s version: 2.0.49\n' % self.name)
                    else:
                        client.send(b'# Unknown command. Try cap, list, nodes, config, fetch, version or quit\n')
                except OSError as err:
                    print("Unable to communicate with client", client, err.__class__, err)
                    client.close()
                    self.clients.remove(client)
            machine.idle()

    def flush(self):
        # close connections:
        for client in self.clients[:]:
            self.clients.remove(client)
            client.close()
        if self.server_socket:
            self.server_socket.close()
        self.server_socket = None

