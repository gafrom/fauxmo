import atexit
from time import sleep
from threading import Thread

# GPIO module is available only on Raspberry device
from RPi import GPIO
# from lib.utils.mock_rpi import GPIO

class Gate:
  def __init__(self, in1_pin, in2_pin, g = GPIO):
    self.g, self.in1, self.in2 = g, in1_pin, in2_pin

    self.g.setmode(self.g.BCM)
    self.g.setup(self.in1, self.g.OUT)
    self.g.setup(self.in2, self.g.OUT)

    # tidy up when leaving
    atexit.register(GPIO.cleanup)

  def right(self, sec = 0.2):
    Thread(target=self.sync_right, args=(sec,)).start()

  def left(self, sec = 0.2):
    Thread(target=self.sync_left, args=(sec,)).start()

  def sync_right(self, sec):
    self.g.output(self.in1, 1)
    self.g.output(self.in2, 0)
    sleep(sec)
    self.g.output(self.in1, 0)

  def sync_left(self, sec):
    self.g.output(self.in1, 0)
    self.g.output(self.in2, 1)
    sleep(sec)
    self.g.output(self.in2, 0)
