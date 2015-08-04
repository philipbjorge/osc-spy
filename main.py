from pythonosc import osc_server
from pythonosc import osc_packet

import threading
import socketserver
import socket

class SimpleUDPClient(object):
  def __init__(self, address, port):
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.setblocking(0)
    self._address = address
    self._port = port

  def send(self, content):
    self._sock.sendto(content, (self._address, self._port))

class UDPForwarderHandler(socketserver.BaseRequestHandler):
  def handle(self):
    data = self.request[0]
    self.server.out.send(data)

    try:
      self.async_print(osc_packet.OscPacket(data))
    except osc_packet.ParseError:
      pass

  def async_print(self, packet):
    thread = threading.Thread(target=self.print, args=(packet, self.server.identifier))
    thread.daemon = True
    thread.start()

  def print(self, packet, identifier):
    for timed_msg in packet.messages:
      vals = ", ".join(map(str, timed_msg.message))
      print("[{0}] [{1}] -- {{{2}}}".format(identifier, timed_msg.message.address, vals))

class OSCUDPServerForwarder(socketserver.UDPServer):
  def __init__(self, identifier, server_address, destination):
    super().__init__(server_address, UDPForwarderHandler)
    self.out = SimpleUDPClient(*destination)
    self.identifier = identifier

  def start(self):
    self.thread = threading.Thread(target=self.serve_forever)
    self.thread.daemon = True
    self.thread.start()


controller_ip = "192.168.0.105"
server_ip = "0.0.0.0"

# Connect lemur outgoing to server_ip:9002, 9002 is arbitrary
# Messages from lemur will be forwarded to server_ip:8002
controller_to_server = OSCUDPServerForwarder("Lemur", (server_ip, 9002), (server_ip, 8002))

# Connect server outgoing to server_ip:8000
# Messages from server will be forwarded to controller_ip:8000
server_to_controller = OSCUDPServerForwarder("Resolume", (server_ip, 8000), (controller_ip, 8000))

controller_to_server.start()
server_to_controller.start()

while True:
  pass
