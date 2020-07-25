import atexit

# GPIO module is available only on Raspberry device
from RPi import GPIO
# from lib.utils.mock_rpi import GPIO

class RelayHandler(object):
  def __init__(self, pin):
    self.pin = pin
    self.pi = GPIO
    self.pi.setmode(self.pi.BCM)
    self.pi.setup(pin, self.pi.OUT)

    # tidy up when leaving
    atexit.register(GPIO.cleanup)

  def on(self):
    # setting it as LOW, because relays are usually "active low"
    self.pi.output(self.pin, 0)
    return True

  def off(self):
    # setting it as HIGH, because relays are usually "active low"
    self.pi.output(self.pin, 1)
    return True

  def state(self):
    # inverting the state because relays are usually "active low"
    return 1 - self.pi.input(self.pin)
