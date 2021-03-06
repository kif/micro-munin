# import dht
import machine
import esp32
import network
from _secret import pin, name, essid
import socket
import select
import sht21

b_essid = essid.encode()
station = network.WLAN(network.STA_IF)


class Node:
    error = b'# Unknown service\n.\n'
    expose = {b"meteo_temperature": b"graph_title SHT21 temperature\n"
                                    b'graph_vlabel degrees Celsius\n'
                                    b'graph_category sensors\n'
                                    b'graph_info This graph shows the temperature sensor of SHT21\n'
                                    b'sht21.info Temperature\n'
                                    b'sht21.min 0\n'
                                    b'sht21.max 70\n'
                                    b'sht21.label Temperature inside\n'
                                    b'esp32.info Temperature\n'
                                    b'esp32.min 0\n'
                                    b'esp32.max 70\n'
                                    b'esp32.label Temperature of the LX6 chip\n'
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
              b"meteo_humidity": b'graph_title SHT21 humidity sensor\n'
                                 b'graph_vlabel % Relative humidity\n'
                                 b'graph_category sensors\n'
                                 b'graph_info This graph shows the relative humidity sensor of the SHT21\n'
                                 b'sht21.info Relative humidity\n'
                                 b'sht21.min 0\n'
                                 b'sht21.max 100\n'
                                 b'sht21.label Humidity inside\n'
                                 b'.\n',
              b"cpuspeed": b'graph_title CPU frequency (MHz)\n'
                           b'graph_category system\n'
                           b'graph_vlabel MHz\n'
                           b'graph_info This graph shows the average running speed of each CPU\n'
                           b'cpu.info Frequency (MHz)\n'
                           b'cpu.max 300\n'
                           b'cpu.min 0\n'
                           b'cpu.label CPU\n'
                           b'.\n',
              b"wifi": b"graph_title Strength of the wifi signal\n"
                       b'graph_vlabel Wifi signal\n'
                       b'graph_category network\n'
                       b'graph_info This graph shows the strength of the WiFi signal\n'
                       b'wifi.info Wifi\n'
                       b'wifi.min 0\n'
                       b'wifi.max 100\n'
                       b'wifi.label Signal strength\n'
                       b'.\n',
              }

    def __init__(self, port=4949, name=name, i2c=None):
        self.i2c = i2c
        self.name = name
        self.addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        print("Munin node %s bound to %s" % (self.name, self.addr))
        self.server_socket = None
        self.clients = []

    def get_list(self):
        return b" ".join(list(self.expose.keys()))

    def get_config(self, what):
        return self.expose.get(what, self.error)

    def fetch(self, what):
        if what == b"meteo_temperature":
            tesp = (esp32.raw_temperature() - 32) * 5 / 9
            tdht = sht21.SHT21_TEMPERATURE(self.i2c)
            return b'esp32.value %.2f\nsht21.value %.2f\n.\n' % (tesp, tdht)
        elif what == b"meteo_humidity":
            return b'sht21.value %.2f\n.\n' % sht21.SHT21_HUMIDITE(self.i2c)
        elif what == b'cpuspeed':
            return b'cpu.value %d\n.\n' % (machine.freq() // 1000000)
        elif what == b'magnetic':
            return b'esp32.value %d\n.\n' % esp32.hall_sensor()
        elif what == b'wifi':
            return b'wifi.value %d\n.\n' % (station.status("rssi") + 100)
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

