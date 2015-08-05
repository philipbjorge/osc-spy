from forwarder import OSCUDPServerForwarder
from collections import defaultdict
import reloading_tabview as t

import logging
logging.disable(logging.CRITICAL)

class OscDataPresenter:
  def __init__(self, serverA, serverB):
    self.serverA = serverA
    self.serverB = serverB

  def cols(self):
    return ["Address", self.serverA.identifier, self.serverB.identifier]

  def data(self):
    d = defaultdict(lambda: list([None, None]))

    for k,v in self.serverA.vals.items():
      d[k][0] = v

    for k,v in self.serverB.vals.items():
      d[k][1] = v

    data = [[k, d[k][0], d[k][1]] for k in sorted(d)]
    data.insert(0, self.cols())
    return data

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

presenter = OscDataPresenter(controller_to_server, server_to_controller)

t.view(presenter.data)
