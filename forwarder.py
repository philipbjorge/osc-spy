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
    thread.daemon = False
    thread.start()

  def print(self, packet, identifier):
    for timed_msg in packet.messages:
      vals = ", ".join(map(str, timed_msg.message))
      self.server.vals[timed_msg.message.address] = vals
      #print("[{0}] [{1}] -- {{{2}}}".format(identifier, timed_msg.message.address, vals))

class OSCUDPServerForwarder(socketserver.UDPServer):
  def __init__(self, identifier, server_address, destination):
    super().__init__(server_address, UDPForwarderHandler)
    self.out = SimpleUDPClient(*destination)
    self.identifier = identifier
    self.vals = {}

  def start(self):
    self.thread = threading.Thread(target=self.serve_forever)
    self.thread.daemon = True
    self.thread.start()
