# name = of the virtual switch
# handler = object with 'on' and 'off' methods
# ip = ip address, defaults to current ip address
# port = port, defaults to 0 (dynamicly assigned)
class Device(object):
  def __init__(self, name, handler, ip = None, port = 0):
    self.name, self.handler, self.ip, self.port = name, handler, ip, port
