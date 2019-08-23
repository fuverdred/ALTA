import time
from pyb import SPI, Pin

from MAX31865 import MAX31865
from MAX31855 import MAX31855

ptd = MAX31865()

spi = SPI(2, mode=SPI.MASTER,
          firstbit=SPI.MSB,
          polarity=0,
          phase=0)
cs = Pin('Y5', Pin.OUT_PP)

k = MAX31855(spi, cs)
