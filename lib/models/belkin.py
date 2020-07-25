import email.utils

from lib.models.upnp_device import UpnpDevice
from lib.utils.logger import logger

# This subclass does the bulk of the work to mimic a WeMo switch on the network.
class Belkin(UpnpDevice):
  # This XML is the minimum needed to define one of our virtual switches
  # to the Amazon Echo
  SETUP_XML = """<?xml version="1.0"?>
  <root>
    <device>
      <deviceType>urn:Belkin:device:controllee:1</deviceType>
      <friendlyName>%(device_name)s</friendlyName>
      <manufacturer>Belkin International Inc.</manufacturer>
      <modelName>Socket</modelName>
      <modelNumber>3.1415</modelNumber>
      <modelDescription>Belkin Plugin Socket 1.0</modelDescription>\r\n
      <UDN>uuid:%(device_serial)s</UDN>
      <serialNumber>221517K0101769</serialNumber>
      <binaryState>0</binaryState>
      <serviceList>
        <service>
          <serviceType>urn:Belkin:service:basicevent:1</serviceType>
          <serviceId>urn:Belkin:serviceId:basicevent1</serviceId>
          <controlURL>/upnp/control/basicevent1</controlURL>
          <eventSubURL>/upnp/event/basicevent1</eventSubURL>
          <SCPDURL>/eventservice.xml</SCPDURL>
        </service>
      </serviceList>
    </device>
  </root>
  """

  @staticmethod
  def make_uuid(name):
      return ''.join(["%x" % sum([ord(c) for c in name])] + ["%x" % ord(c) for c in "%sfauxmo!" % name])[:14]

  def __init__(self, name, listener, poller, ip_address, port, action_handler):
      self.serial = self.make_uuid(name)
      self.name = name
      self.ip_address = ip_address
      self.action_handler = action_handler
      logger.debug("IP: %s" % ip_address)
      persistent_uuid = "Socket-1_0-" + self.serial
      other_headers = ['X-User-Agent: redsonic']
      super().__init__(listener, poller, port, "http://%(ip_address)s:%(port)s/setup.xml", "Unspecified, UPnP/1.0, Unspecified", persistent_uuid, other_headers=other_headers, ip_address=ip_address)

      logger.debug("FauxMo device '%s' ready on %s:%s" % (self.name, self.ip_address, self.port))

  def get_name(self):
      return self.name

  def handle_request(self, data, sender, socket):
      # called once to setup connection when discovering a device
      if data.find('GET /setup.xml HTTP/1.1') == 0:
          logger.debug("Responding to setup.xml for %s" % self.name)
          xml = self.SETUP_XML % {'device_name' : self.name, 'device_serial' : self.serial}
          date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
          message = ("HTTP/1.1 200 OK\r\n"
                     "CONTENT-LENGTH: %d\r\n"
                     "CONTENT-TYPE: text/xml\r\n"
                     "DATE: %s\r\n"
                     "LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT\r\n"
                     "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                     "X-User-Agent: redsonic\r\n"
                     "CONNECTION: close\r\n"
                     "\r\n"
                     "%s" % (len(xml), date_str, xml))
          self._send_message(socket, message)

      # called to toggle state
      elif data.find('SOAPACTION: "urn:Belkin:service:basicevent:1#SetBinaryState"') != -1:
          logger.debug("Responding to SOAPACTION:set")
          success = False
          soap = ''
          if data.find('<BinaryState>1</BinaryState>') != -1:
              # on
              logger.debug("Responding to ON for %s" % self.name)
              soap = self._soap('set', 1)
              success = self.action_handler.on()
          elif data.find('<BinaryState>0</BinaryState>') != -1:
              # off
              logger.debug("Responding to OFF for %s" % self.name)
              soap = self._soap('set', 0)
              success = self.action_handler.off()
          else:
              logger.debug("[ERROR] Unknown Binary State request:")
              logger.debug(data)
          if success:
              date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
              message = ("HTTP/1.1 200 OK\r\n"
                         "CONTENT-LENGTH: %d\r\n"
                         "CONTENT-TYPE: text/xml charset=\"utf-8\"\r\n"
                         "DATE: %s\r\n"
                         "EXT:\r\n"
                         "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                         "X-User-Agent: redsonic\r\n"
                         "CONNECTION: close\r\n"
                         "\r\n"
                         "%s" % (len(soap), date_str, soap))
              self._send_message(socket, message)
              logger.debug("Send response to SOAPACTION:set\r\n" + message)
      # called (a) to complete the discovery of a device, (b) later on to get a state
      elif data.find('SOAPACTION: "urn:Belkin:service:basicevent:1#GetBinaryState"') != -1:
          logger.debug("Responding to SOAPACTION:get")

          state = self.action_handler.state()
          soap = self._soap('get', state)
          date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
          message = ("HTTP/1.1 200 OK\r\n"
                     "CONTENT-LENGTH: %d\r\n"
                     "CONTENT-TYPE: text/xml charset=\"utf-8\"\r\n"
                     "DATE: %s\r\n"
                     "EXT:\r\n"
                     "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                     "X-User-Agent: redsonic\r\n"
                     "CONNECTION: close\r\n"
                     "\r\n"
                     "%s" % (len(soap), date_str, soap))
          self._send_message(socket, message)
          logger.debug("Send response to SOAPACTION:get\r\n" + message)
      else:
          logger.debug("[ERROR] Unknown request:\r\n")
          logger.debug(data)

  def _soap(self, method, state):
    method = method.capitalize()

    return ("<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body>\r\n"
            "<u:%sBinaryStateResponse xmlns:u=\"urn:Belkin:service:basicevent:1\">\r\n"
            "<BinaryState>%s</BinaryState>\r\n"
            "</u:%sBinaryStateResponse>\r\n"
            "</s:Body></s:Envelope>\r\n" % (method, state, method))
