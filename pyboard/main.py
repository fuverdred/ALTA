import time
from pyb import SPI, Pin, millis

from MAX31865 import MAX31865
from MAX31855_corrected import MAX31855

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
spi_K = SPI(2, # pyBoard harware SPI 2 (Y5, Y6, Y7, Y8)
            mode=SPI.MASTER,
            baudrate=100000,
            polarity=0,
            phase=0,
            firstbit=SPI.MSB)
cs_K = Pin('Y5', Pin.OUT_PP) # Chip select pin

k = MAX31855(spi_K, cs_K)

## SETUP RELAY
# In current set-up relay 1 on cools, relay 2 on heats

relay_1 = Pin('X12', mode=Pin.OUT_PP)
relay_1(True) # Closed
relay_2 = Pin('X11', mode=Pin.OUT_PP)
relay_2(True) # Closed

## SETUP LDR

ldr_pin = pyb.ADC(Pin('Y11'))



def collect_data(filename, duration=600):
    with open(filename, 'w') as f:
        start = time.time()
        while time.time() - start < duration:
            t = time.time() - start
            k_temp = k.read()
            ptd_temp = ptd.read()
            s = ','.join([str(i) for i in (t, k_temp, ptd_temp)]) + '\n'
            _ = f.write(s)
            print(s)
            time.sleep(1)

def weak_temp_control(filename, duration=600, target=-10):
    '''
    Enter a file name to save data to and a duration in seconds
    '''
    start = millis()
    duration *= 1000 # convert seconds to milliseconds
    relay_1(False) # Start cooling
    with open(filename, 'w') as f:
        while(millis() - start < duration):
            temp = ptd.read()
            k_temp = k.read()
            t = millis() - start
            print(t, '\t', temp, '\t', k_temp)
            if temp < target and not relay_1.value():
                relay_1(True) # stop cooling
            elif temp > target and relay_1.value():
                relay_1(False) # start cooling
            f.write(','.join([str(i) for i in (t, temp, k_temp)]) + '\n')
            time.sleep_ms(100)
        relay_1(True) # Stop Cooling
                

def LDR_temp_dependence(filename, duration=600):
    '''
    Enter a file name to save data to and a duration in seconds
    '''
    start = time.time()
    relay_1(False) # Start cooling
    with open(filename, 'w') as f:
        while time.time() - start < duration:
            temp = k.read()
            t = time.time() - start
            ldr = ldr_pin.read()
            print(t, '\t', temp, '\t', ldr)
            f.write(','.join([str(i) for i in (t, temp, ldr)]) + '\n')
            time.sleep(1)

def freeze_testing(filename):
    relay_1(False) #  start cooling
    start = millis()
    t = start
    with open('data/intensity_freeze_melt.csv', 'w') as f:
        while t < 200000:
            t = millis() - start
            T = ptd.read()
            ldr = ldr_pin.read()
            s = ','.join([str(i) for i in (t, T, ldr)])
            print(s)
            _ = f.write(s + '\n')
        relay_1(True)
        while T < 18:
            t = millis() - start
            T = ptd.read()
            ldr = ldr_pin.read()
            s = ','.join([str(i) for i in (t, T, ldr)])
            print(s)
            _ = f.write(s + '\n')
            
            
            
        
    

