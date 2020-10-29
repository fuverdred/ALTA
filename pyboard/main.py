import time, os
from pyb import SPI, Pin, millis, Timer, I2C

from MAX31865 import MAX31865
from MAX31855 import MAX31855
from pyb_i2c_lcd import I2cLcd
from ALTA import ALTA

##  INITIALISE PLATINUM RESISTANCE THERMOMETER (MAX31865)
spi_PTD = SPI(1, # pyBoard hardware SPI 1 (X5, X6, X7, X8)
              mode=SPI.MASTER,
              baudrate=100000,
              polarity=0,
              phase=1,
              firstbit=SPI.MSB)
cs_PTD = Pin('X5', mode=Pin.OUT_PP) # Chip select pin

ptd = MAX31865(spi_PTD, cs_PTD)


## INITIALISE K TYPE THERMOCOUPLE (MAX31855)
'''
spi_K = SPI(2, # pyBoard harware SPI 2 (Y5, Y6, Y7, Y8)
            mode=SPI.MASTER,
            baudrate=100000,
            polarity=0,
            phase=0,
            firstbit=SPI.MSB)
cs_K = Pin('Y5', Pin.OUT_PP) # Chip select pin

k = MAX31855(spi_K, cs_K)
'''

## INITIALISE INNER PTD
spi_inner = SPI(2, # pyBoard hardware SPI 1 (X5, X6, X7, X8)
              mode=SPI.MASTER,
              baudrate=100000,
              polarity=0,
              phase=1,
              firstbit=SPI.MSB)
cs_inner = Pin('Y5', mode=Pin.OUT_PP) # Chip select pin

inner = MAX31865(spi_inner, cs_inner)

## SETUP LDR

ldr_pin = pyb.ADC(Pin('Y12'))

## SETUP PWM

pwm_pin = Pin('Y4')
tim = Timer(4, freq=100)
ch = tim.channel(4, Timer.PWM, pin=pwm_pin)
ch.pulse_width_percent(0)

## SETUP FAN CONTROL

fans_pin = Pin('Y3', mode=Pin.OUT_PP)
fans_pin.low()

## SETUP LCD
lcd_address = 0x3F
i2c = I2C(1, I2C.MASTER)
lcd = I2cLcd(i2c, lcd_address, 2, 16)

## SETUP RELAY
relay_1 = Pin('X11', mode=Pin.OUT_PP)
relay_2 = Pin('X12', mode=Pin.OUT_PP)

## SETUP STATE MACHINE
alta = ALTA(ptd,
            inner,
            ch,
            ldr_pin,
            lcd,
            fans_pin,
            relay_1,
            relay_2)

filepath = 'data/linear_test'

#alta.linear_experiment(filepath)
  
