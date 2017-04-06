from inz.coordinates import Coordinates
from bluetooth import *

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

yacht_coordinates = Coordinates()
buoy_coordinates = Coordinates()

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service(server_sock, "TestServer",
                  service_id=uuid,
                  service_classes=[uuid, SERIAL_PORT_CLASS],
                  profiles=[SERIAL_PORT_PROFILE])

print("Waiting for connection on RFCOMM channel %d" % port)
client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

while True:
    try:
        req = client_sock.recv(1024)
        type(req)
        if len(req) == 0:
            break
        yacht_coordinates.set_coordinates([float(req.split()[0]), float(req.split()[1])])
        buoy_coordinates.set_random_buoy_coordinates(yacht_coordinates)
        print(yacht_coordinates)
        data = str(buoy_coordinates)
        print(data)
        if data:
            print("sending [%s]" % data)
            client_sock.send(data)

    except IOError:
        print("IOERROR")

    except KeyboardInterrupt:

        print("disconnected")

        client_sock.close()
        server_sock.close()
        print("all done")

        break
