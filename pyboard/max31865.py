from machine import SPI, Pin
import ustruct

class MAX31865():

   ### Register constants, see data sheet for info.
   # Read Addresses
   MAX31865_REG_READ_CONFIG  = 0x00
   MAX31865_REG_READ_RTD_MSB = 0x01
   MAX31865_REG_READ_RTD_LSB = 0x02
   MAX31865_REG_READ_HFT_MSB = 0x03
   MAX31865_REG_READ_HFT_LSB = 0x04
   MAX31865_REG_READ_LFT_MSB = 0x05
   MAX31865_REG_READ_LFT_LSB = 0x06
   MAX31865_REG_READ_FAULT   = 0x07

   # Write Addresses
   MAX31865_REG_WRITE_CONFIG  = 0x80
   MAX31865_REG_WRITE_HFT_MSB = 0x83
   MAX31865_REG_WRITE_HFT_LSB = 0x84
   MAX31865_REG_WRITE_LFT_MSB = 0x85
   MAX31865_REG_WRITE_LFT_LSB = 0x86

   # Configuration Register
   MAX31865_CONFIG_50HZ_FILTER = 0x01
   MAX31865_CONFIG_CLEAR_FAULT = 0x02
   MAX31865_CONFIG_3WIRE       = 0x10
   MAX31865_CONFIG_ONE_SHOT    = 0x20
   MAX31865_CONFIG_AUTO        = 0x40
   MAX31865_CONFIG_BIAS_ON     = 0x80

   def __init__(self, spi, cs_pin, wires=2):
      self.cs_pin = cs_pin
      self.cs_pin(True) # Set high immediately
      self.spi = spi
      self.wires = wires

      # set configuration register
      config = (self.MAX31865_CONFIG_BIAS_ON +
                self.MAX31865_CONFIG_AUTO +
                self.MAX31865_CONFIG_CLEAR_FAULT +
                self.MAX31865_CONFIG_50HZ_FILTER)
      if (self.wires == 3):
          config += MAX31865_CONFIG_3WIRE

      buf = bytearray(2)
      buf[0] = self.MAX31865_REG_WRITE_CONFIG  # config write address
      buf[1] = config
      self.cs_pin(False) # Select chip
      _ = self.spi.send(buf) # write config
      self.cs_pin(True)

      self.RefR = 400.0 # Ohms, this is R7 on the board
      self.R0  = 100.0 # Ohms, Using a PT100

   def _RawToTemp(self, raw):
      '''
      In our temperature range the resistance is very linear.
      Using the IEC 751 standard, alpha is 0.00385, y intercept = 100
      '''
      RTD = (raw * self.RefR) / (32768) # 32768=2^15
      m = 0.385 # Ohms/degC
      return (1/m) * (RTD - 100), RTD

   def read(self):
      raw = bytearray(2)
      self.cs_pin(False) # Select chip
      _ = self.spi.send(bytes([0x01])) # first read address
      raw = self.spi.recv(2)           # multi-byte transfer
      self.cs_pin(True)

      raw_int = ustruct.unpack('>H', raw)[0]
      raw_int >>= 1 # fifteen bit integer is sent
      temp, RTD = self._RawToTemp(raw_int)
      temp = float('%.1f'%temp) # trim to 1 decimal place
      return temp
