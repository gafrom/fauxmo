from lib.utils.logger import logger

class GPIO:
  BCM = 'BCM'
  OUT = 'OUT'

  @staticmethod
  def setmode(*args):
    logger.debug("===> setmode: " + str(args))

  def input(*args):
    logger.debug("===> input: " + str(args))
    return 0

  def output(*args):
    logger.debug("===> output: " + str(args))

  def setup(*args):
    logger.debug("===> setup: " + str(args))

  def cleanup():
    logger.debug("===> cleanup.")
