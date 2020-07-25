import socket
import email.utils
import uuid

from lib.utils.logger import logger

# Base class for a generic UPnP device. This is far from complete
# but it supports either specified or automatic IP address and port
# selection.
class UpnpDevice:
  this_host_ip = None

  @staticmethod
  def local_ip_address():
    if not UpnpDevice.this_host_ip:
      temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        temp_socket.connect(('8.8.8.8', 53))
        UpnpDevice.this_host_ip = temp_socket.getsockname()[0]
      except:
        UpnpDevice.this_host_ip = '127.0.0.1'
      del(temp_socket)
      logger.debug("got local address of %s" % UpnpDevice.this_host_ip)

    return UpnpDevice.this_host_ip

  def __init__(self, listener, poller, port, root_url, server_version, persistent_uuid, other_headers = None, ip_address = None):
    self.listener = listener
    self.poller = poller
    self.port = port
    self.root_url = root_url
    self.server_version = server_version
    self.persistent_uuid = persistent_uuid
    self.uuid = uuid.uuid4()
    self.other_headers = other_headers
    self.ip_address = ip_address if ip_address else self.local_ip_address()
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((self.ip_address, self.port))
    self.socket.listen(5)
    if self.port == 0:
      self.port = self.socket.getsockname()[1]
    self.poller.add(self)
    self.client_sockets = {}
    self.listener.add_device(self)

  def fileno(self):
    return self.socket.fileno()

  def do_read(self, fileno):
    if fileno == self.socket.fileno():
      (client_socket, client_address) = self.socket.accept()
      self.poller.add(self, client_socket.fileno())
      self.client_sockets[client_socket.fileno()] = client_socket
    else:
      data, sender = self.client_sockets[fileno].recvfrom(4096)
      if not data:
        self.poller.remove(self, fileno)
        del(self.client_sockets[fileno])
      else:
        self.handle_request(data.decode('ascii'), sender, self.client_sockets[fileno])

  def handle_request(self, data, sender, socket):
    pass

  def get_name(self):
    return "unknown"
      
  def respond_to_search(self, destination):
    logger.debug("Responding to search for %s" % self.get_name())
    date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
    location_url = self.root_url % {'ip_address' : self.ip_address, 'port' : self.port}
    message = ("HTTP/1.1 200 OK\r\n"
              "CACHE-CONTROL: max-age=86400\r\n"
              "DATE: %s\r\n"
              "EXT:\r\n"
              "LOCATION: %s\r\n"
              "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
              "01-NLS: %s\r\n"
              "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
              "ST: urn:Belkin:device:**\r\n"
              "USN: uuid:%s::upnp:rootdevice\r\n"
              "X-User-Agent: redsonic\r\n\r\n" % (date_str, location_url, self.uuid, self.persistent_uuid))
    if self.other_headers:
      for header in self.other_headers:
        message += "%s\r\n" % header
    message += "\r\n"
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_socket.sendto(self._encode(message), destination)

  def _send_message(self, socket, message):
    return socket.send(self._encode(message))

  def _encode(self, text):
    return text.encode('ascii')
