import socket
import struct
import time

from lib.utils.logger import logger

# Since we have a single process managing several virtual UPnP devices,
# we only need a single listener for UPnP broadcasts. When a matching
# search is received, it causes each device instance to respond.
#
# Note that this is currently hard-coded to recognize only the search
# from the Amazon Echo for WeMo devices. In particular, it does not
# support the more common root device general search. The Echo
# doesn't search for root devices.
class UpnpBroadcastResponder:
  TIMEOUT = 0

  def __init__(self):
    self.devices = []

  def init_socket(self):
    self.ip = '239.255.255.250'
    self.port = 1900

    for attempt in range(15):
      ok = True
      try:
        #This is needed to join a multicast group
        self.mreq = struct.pack("4sl",socket.inet_aton(self.ip),socket.INADDR_ANY)

        #Set up server socket
        self.ssock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.ssock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.ssock.bind(('', self.port))
        self.ssock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,self.mreq)

        break
      except Exception as e:
        ok = False
        logger.debug("Failed %s attempt to initialize UPnP sockets: %s" % (attempt, e))
        time.sleep(1.5**attempt) # the max is 1.5**15 = 7 minutes of wait time
        continue

    if ok:
      logger.debug("Listening for UPnP broadcasts")
      return True

    raise Exception("[ERROR] Failed to initialize a socket")

  def close_socket(self):
    # self.ssock.shutdown(socket.SHUT_RDWR)
    self.ssock.close()

  def fileno(self):
    return self.ssock.fileno()

  def do_read(self, fileno):
    logger.debug("reading")
    data, sender = self.recvfrom(1024)
    if data:
      logger.debug("data: %s" % (data))
      if data.find('M-SEARCH') == 0 and data.find('upnp:rootdevice') != -1:
        for device in self.devices:
          time.sleep(0.1)
          device.respond_to_search(sender)

  #Receive network data
  def recvfrom(self,size):
    if self.TIMEOUT:
      self.ssock.setblocking(0)
      ready = select.select([self.ssock], [], [], self.TIMEOUT)[0]
    else:
      self.ssock.setblocking(1)
      ready = True

    try:
      if ready:
        data, receiver = self.ssock.recvfrom(size)
        return data.decode('ascii'), receiver
      else:
        return False, False
    except Exception as e:
      logger.debug(e)
      return False, False

  def add_device(self, device):
    self.devices.append(device)
    logger.debug("UPnP broadcast listener: new device registered")
