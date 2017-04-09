from inz.coordinates import Coordinates
from bluetooth import *
import time

_UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"


class BluetoothServer:
    """ This class represents server in bluetooth communication."""

    def __init__(self, yacht_coordinates, buoy_coordinates):
        """ This function initializes communication between server and client.

        :param yacht_coordinates: represents coordinates of a yacht received from client's application
        :param buoy_coordinates: represents coordinates of detected buoy
        """

        self.yacht_coordinates = yacht_coordinates
        self.buoy_coordinates = buoy_coordinates

        # initialize socket using Radio Frequency Communication protocol
        self.server_sock = BluetoothSocket(RFCOMM)
        # bind server socket to any port
        self.server_sock.bind(("", PORT_ANY))
        # listening on binded socket
        self.server_sock.listen(1)
        # return port number on which server socket is bound
        self.port = self.server_sock.getsockname()[1]

        # spread out bluetooth server
        advertise_service(self.server_sock, "YachtRacingSupport bluetooth server",
                          service_id=_UUID,
                          service_classes=[_UUID, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE])

        print("Waiting for connection on RFCOMM channel %d" % self.port)
        self.client_sock, client_info = self.server_sock.accept()
        print("Accepted connection from ", client_info)

    def handle_data(self):
        """ This function handles data which are exchanged in bluetooth communication.

        Received data are construed as yacht's longitude, latitude and azimuth.
        Sent data are coordinates of a buoy detected on camera image.
        """
        while True:
            try:
                # receive data from client socket
                req = self.client_sock.recv(1024)

                # break if there is no data
                if len(req) == 0:
                    break

                # split received data
                req = req.split()
                # set yacht coordinates with received data
                self.yacht_coordinates.set_coordinates([float(req[0]), float(req[1])], float(req[2]))
                # set buoy coordinates with yacht coordinates with random generated shift
                self.buoy_coordinates.set_random_buoy_coordinates(self.yacht_coordinates)
                # prepare data to send
                data = str(self.buoy_coordinates)
                # if buoy coordinates exist (buoy has been detected)
                if data:
                    # sending buoy coordinates
                    self.client_sock.send(data)
                # force thread sleep
                time.sleep(1)

            except IOError:
                # Input/Output error!
                print("IOERROR")

            except KeyboardInterrupt:
                # Closing sockets.
                self.client_sock.close()
                self.server_sock.close()
                break
