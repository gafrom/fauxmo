from lib.models.gate import Gate

class GateHandler(object):
  def __init__(self, in1_pin, in2_pin):
    self.gate = Gate(in1_pin, in2_pin)
    self._state = 0
 
  def on(self):
    self.gate.left(5.7)
    self._state = 1
    return True

  def off(self):
    self.gate.right(5.1)
    self._state = 0
    return True

  def state(self):
    return self._state
