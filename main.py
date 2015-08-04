from forwarder import OSCUDPServerForwarder
import npyscreen
from collections import defaultdict

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

    data = [item for k in sorted(d) for item in (k, d[k][0], d[k][1])]
    return data

class OscSpyApp(npyscreen.NPSAppManaged):
  def onStart(self):
    self.mainForm = self.addForm('MAIN', MainForm)

class MainForm(npyscreen.Form):
  def create(self):
    self.keypress_timeout = 10
    self.presenter = OscDataPresenter(controller_to_server, server_to_controller)
    cols = self.presenter.cols()
    self.grid = self.add(npyscreen.GridColTitles, col_titles=cols, select_whole_line=True, columns=len(cols))

  def while_waiting(self):
    self.grid.set_grid_values_from_flat_list(self.presenter.data(), reset_cursor=False)
    self.grid.display()

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

OscSpyApp().run()
