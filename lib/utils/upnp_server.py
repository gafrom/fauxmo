import atexit
import time

from lib.models.belkin import Belkin
from lib.utils.poller import Poller
from lib.utils.upnp_broadcast_responder import UpnpBroadcastResponder
from lib.utils.logger import logger

class UpnpServer:
  def __init__(self, devices):
    self.devices = devices

    # Set up our singleton for polling the sockets for data ready
    self.poller = Poller()
    self.responder = UpnpBroadcastResponder()

  def start(self):
    # Set up our singleton listener for UPnP broadcasts
    self.responder.init_socket()

    # Add the UPnP broadcast listener to the poller so we can respond
    # when a broadcast is received.
    self.poller.add(self.responder)

    # Create our FauxMo virtual switch devices
    for device in self.devices:
      Belkin(device.name, self.responder, self.poller, device.ip, device.port, device.handler)

    atexit.register(self.responder.close_socket)

    logger.debug("Entering main loop\n")

    while True:
      try:
        # Allow time for a ctrl-c to stop the process
        self.poller.poll(100)
        time.sleep(0.1)
      except Exception as e:
        logger.debug(e)
        break
