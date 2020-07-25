#!/usr/bin/env python3

from lib.utils.upnp_server import UpnpServer
from lib.models.device import Device
from lib.handlers.relay_handler import RelayHandler
from lib.handlers.gate_handler import GateHandler

# The Echo appears to have a hard-coded limit of 16 switches it can control.
# Only the first 16 elements of the list will be used.
devices = (
  Device('kitchen5', RelayHandler(17),    None, 54545),
  Device('gate',     GateHandler(23, 24), None, 54546)
)

server = UpnpServer(devices)
server.start()
