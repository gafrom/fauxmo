import sys
import logging

logging.basicConfig(level=logging.DEBUG if len(sys.argv) > 1 and sys.argv[1] == '-d' else logging.WARN)
logger = logging.getLogger('Fauxmo')
