from lib.models.gate import Gate

class GateHandler(object):
  def __init__(self, in1_pin, in2_pin):
    self.gate = Gate(in1_pin, in2_pin)
    self._state = 0
 
  def on(self):
    duration = 5.7 if self._state == 0 else 1

    self.gate.left(duration)
    self._state = 1
    return True

  def off(self):
    duration = 5.2 if self._state == 1 else 1

    self.gate.right(duration)
    self._state = 0
    return True

  def state(self):
    return self._state
