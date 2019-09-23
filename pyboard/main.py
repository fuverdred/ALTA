import time
from pyb import SPI, Pin, millis, Timer
import uheapq

from MAX31865 import MAX31865
from MAX31855_corrected import MAX31855
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

## SETUP PWM

pwm_pin = Pin('X10')
tim = Timer(4, freq=1000)
ch = tim.channel(2, Timer.PWM, pin=pwm_pin)
ch.pulse_width_percent(0)

## SETUP STATE MACHINE
alta = ALTA(ptd, k, ch, relay_1, relay_2)


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


            
def latent_heat(filename, limit=-15, queue_length=5):
    queue = []
    frozen = False
    with open('data/'+filename, 'w') as f:
        relay_1(False) #  Start cooling
        start = millis()
        while not frozen:
            t = millis() - start
            T = ptd.read()
            ldr = ldr_pin.read()
            
            
            if T < limit and not relay_1.value():
                relay_1(True)
            elif relay_1.value():
                relay_1(False)

            if len(queue) == queue_length:
                if T - queue.pop(0) > 0.3:
                    print("FROZEN")
                    frozen = True # break out of this loop
            queue.append(T)
            
            print(t, '\t', T)
            _ = f.write(','.join([str(i) for i in (t, T, ldr)])+'\n')
            
            time.sleep_ms(100)
        relay_1(True) #  Stop cooling
        relay_2(False) # Heating
        while T < 15:
            t = millis() - start
            T = ptd.read()
            ldr = ldr_pin.read()
            print(t, '\t', T)
            _ = f.write(','.join([str(i) for i in (t, T, ldr)])+'\n')
            time.sleep_ms(100)
        relay_2(True)

def thermal_calibration(filename, profile):
    with open('data/'+filename, 'w') as f:
        start = millis()
        for target_T, wait_period in profile:
            wait_period *= 1000
            profile_start = millis() - start
            t = millis() - start
            print('Target Temperature: ', target_T)
            while t - profile_start < wait_period:
                T = ptd.read()
                T_k = k.read()
                t = millis() - start

                if T > target_T and relay_1.value():
                    relay_1(False) # start cooling
                elif T < target_T and not relay_1.value():
                    relay_1(True)

                print(t, '\t', T, '\t', T_k)
                _ = f.write(','.join([str(i) for i in (t, T, T_k)])+'\n')
                time.sleep_ms(100)
        relay_1(True)
                

                
            
        



example_profile = [(0, 300),
                   (-5, 300),
                   (-10, 300),
                   (-15, 300),
                   (-20, 300)]


def PWM_test(filename):
    with open('data/'+filename, 'w') as f:
        start = time.time()
        relay_1(False)
        ch.pulse_width_percent(100)
        while time.time() - start < 500:
            t = time.time()
            T = ptd.read()
            T_k = k.read()
            print(t,'\t', T, '\t', T_k)
            _ = f.write(','.join([str(i) for i in (t, T, T_k)])+'\n')
            time.sleep(1)
    relay_1(True)
    ch.pulse_width_percent(0)

def thingy_test(filename):
    start = millis()
    pw = 60

    t = millis()
    T = ptd.read()
    T_k = k.read()
    
    ch.pulse_width_percent(pw)
    relay_1(False)
    
    with open('data/' + filename, 'w') as f:
        while t < start + 600 * 1000:
            t = millis()
            T = ptd.read()
            T_k = k.read()
            _ = f.write(','.join([str(i) for i in (t, pw, T, T_k)]) + '\n')
            print(t, '\t', T, '\t', T_k)
            time.sleep(1)

        print('Going to 100% pulse width')
        pw = 70
        ch.pulse_width_percent(pw)
        while t < start + (600 + 600) * 1000:
            t = millis()
            T = ptd.read()
            T_k = k.read()
            _ = f.write(','.join([str(i) for i in (t, pw, T, T_k)]) + '\n')
            print(t, '\t', T, '\t', T_k)
            time.sleep(1)

        print('Going to 0% pulse width')
        pw = 50
        ch.pulse_width_percent(pw)
        while t < start + (600 + 600 + 600)*1000:
            t = millis()
            T = ptd.read()
            T_k = k.read()
            _ = f.write(','.join([str(i) for i in (t, pw, T, T_k)]) + '\n')
            print(t, '\t', T, '\t', T_k)
            time.sleep(1)

        print('Going back to 50% pulse width')
        pw = 60
        ch.pulse_width_percent(pw)
        while t < start + (600 + 600 + 600 + 600) * 1000:
            t = millis()
            T = ptd.read()
            T_k = k.read()
            _ = f.write(','.join([str(i) for i in (t, pw, T, T_k)]) + '\n')
            print(t, '\t', T, '\t', T_k)
            time.sleep(1)

#thingy_test('thingy_test.csv')
    

