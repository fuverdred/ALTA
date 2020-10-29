'''
======================================================
Automated Lag-Time Apparatus (ALTA)
======================================================

This is the main library for ALTA, stored on github.com/fuverdred/ALTA

## INPUTS & OUTPUTS

Inputs:
1. Aluminium body temperature from a platinum resistance thermometer drilled
into the aluminium just below the sample vial.
2. A light dependent resistor (LDR) value which dictataes whether or not
the sample is frozen.

Outputs:
1. Relay settings. These control the direction of the flow of current as
follows:
                relay 1 |   on    | off
                --------+-------------------
        relay 2     on  |    -    |  Heating
                    off | Cooling |     -
                    
2. Pulse width modulation (PWM) percentage duty cycle, which is smoothed to
an approximate DC current (maximum 0.5A ripple)
3. Fans. These are turned on for cooling and off for the rest as they are
loud and annoying
4. LCD screen for displaying the current status of ALTA


## OUTPUT FORMAT
While an experimental repeat is running the data is written to a file called
running.csv.

After completion of the run the file is renamed to reflect the outcome of
the run, using the following format:

1. Repeat number
2. Experiment type (isothermal, linear)
    2.1 Experiment temperature (isothermal) or rate (linear)
    2.2 Outcome (early, frozen, liquid) # isothermal only
3. Time to freeze (ms)/ frozen temperature (deg C) # isothermal/linear

eg. 23_isothermal_-15.0_frozen_34200.csv
Which is the 23rd repeat of an isothermal experiment at -15.0 deg C, which
froze after 34200 ms at the target temperature.

Each file contains the following columns, separated by commas:
1. Time (ms)
2. Aluminium temperature (deg C)
    2.1 Internal temperature (deg C) for calibration
3. LDR value (Arb units)
4. ALTA status (cool, hold, heat)
'''

import os
import time
from pyb import SPI, Pin, millis, Timer

from pi_controller import PI_Controller


class ALTA():
    LDR_THRESHOLD = 150 # 150 less than the clear LDR value
    MAXIMUM_WAIT = 1000 * 60 * 2.5 #1000 * 60 * 60 * 2 # (ms) 2 hours in ms
    # PWM_FIT_COEFFS is a polynomial to approximate the temperature at any
    # given PWM value. This is for isothermal experiments to approx the offset
    PWM_FIT_COEFFS = (32.913, -1.623, 0.014) # magic numbers
    DELAY_MS = 200 # (ms), time between readings
    DELAY_S = DELAY_MS / 1000 # (s)
    MELT_TEMPERATURE = 15 # (deg C) Temperature to hold at while sample melts
    MELT_TIME = 1000 * 60 # (ms) Wait 1 minute

    K_C = -10 #  Proportional constant for PI control
    TAU_I = 100 #  Integrational time constant for PI control
    
    def __init__(self,
                 ptd,
                 calibrate,
                 pwm_channel,
                 ldr_pin,
                 lcd,
                 fans_pin,
                 relay_1,
                 relay_2):
        '''
        ptd: platinum resistance thermometer (ptd) embedded in ALTA (MAX31865)
        calibrate: ptd which can be placed inside sample for calibration
        pwm_channel: A timer instance allowing PWM duty cycle to be set
        ldr_pin: Analogue read instance for measuring LDR resistance
        lcd: pyb_lcd_i2c instance for displaying messages on the LCD
        fans_pin: GPIO pin for switching fans on and off
        relay_1: GPIO pin for switching relay 1
        relay_2: GPIO pin for switching relay 2
        '''
        self.ptd = ptd # MAX31865 
        self.calibrate = calibrate # MAX31865
        self.pwm_channel = pwm_channel # Timer channel instance
        self.ldr_pin = ldr_pin # Analogue read instance
        self.lcd = lcd # pyb_lcd_i2c instance
        self.fans_pin = fans_pin # GPIO 
        self.relay_1 = relay_1 # GPIO
        self.relay_2 = relay_2 # GPIO
        
        self.switch_off()
        self.screen_put("LET'S FREEZE") # Welcome message

    def switch_off(self):
        '''Turn off all outputs, switch relay to cooling'''
        self.fans_pin.low() # Fans off
        self.pwm_channel.pulse_width_percent(0) # Peltiers off
        self.relay_cool() # Current direction to cool

    def screen_put(self, message='', row=0):
        '''Display a message on the LCD screen'''
        self.lcd.move_to(0, row)
        self.lcd.putstr('{:^16}'.format(message)) # Always centred

    def read_inputs(self):
        '''Read all ALTA inputs, return them as (temp, calibrate, ldr) tuple'''
        temp = self.ptd.read()
        calibrate = self.calibrate.read()
        ldr = self.ldr_pin.read()
        return temp, calibrate, ldr

    def relay_cool(self):
        '''Set current in cooling direction'''
        self.pwm_channel.pulse_width_percent(0) #  Avoid hot switching
        self.relay_1.low()
        self.relay_2.high()

    def relay_heat(self):
        '''Set current in heating direction'''
        self.pwm_channel.pulse_width_percent(0) #  Avoid hot switching
        self.relay_1.high()
        self.relay_2.low()

    def flip_relay(self):
        '''Reverse current direction'''
        self.pwm_channel.pulse_width_percent(0) #  Avoid hot switching
        self.relay_1.toggle()
        self.relay_2.toggle()
        

    def target_pwm(self, limit):
        '''
        Uses an empirically calculated polynomial fit to find the approximate
        PWM necessary to maintain the limit temperature
        '''
        return sum([coeff * (limit**i)
                    for i, coeff in enumerate(self.PWM_FIT_COEFFS)])

    def overshoot(self, limit):
        '''
        In isothermal experiments at higher temperatures allow the aluminium
        to get colder than the target temperature, as the sample lags behind.

        This is a linear function of target temperature, with lower temperatures
        having a smaller overshoot
        '''
        if limit < -25 or limit > 0:
            return 0 # not optimised for T > 0, no offset for T < -25
        else:
            overshoot = 0.05*limit + 1.25 # Simple linear function
            return ((10*overshoot)//1)/10 # Return 1 decimal place

    def set_pwm(self, pwm):
        '''Set pulse width duty cycle. If > 0 the fans are switched on'''
        pwm = int(pwm)
        if not 0 <= pwm <= 100:
            pwm = 0
        self.pwm_channel.pulse_width_percent(pwm)
        if pwm == 0:
            self.fans_pin.low() # Turn off fans
        else:
            self.fans_pin.high()

    def timer(self):
        '''Yields time in ms since timer was started'''
        start = millis()
        while True:
            yield millis() - start # Not protected against roll-overs

    def csvify(self, *args):
        '''Convert all args to a string delimited by commas'''
        return ','.join([str(arg) for arg in args])+'\n'

    def get_repeat_number(self, filepath):
        '''Find the number of the most recent repeat in the filepath'''
        files = [f for f in os.listdir(filepath) if 'running' not in f]
        if files == []:
            return 0
        return max([int(file.split('_')[0]) for file in files])

    def melt(self, timer):
        '''
        Heat the sample to a target temperature, then hold at that temp
        for a specified amount of time.
        '''
        status = 'Heat'
        self.relay_heat()
        self.set_pwm(100)

        t = next(timer)
        wait_end = t + self.MELT_TIME
        heat_flag = True
        while t < wait_end:
            t = next(timer)
            T, _, _ = self.read_inputs()

            self.screen_put('{} {:5.1f} {:5d}'.format(status,
                                                      T,
                                                      t//1000), # ms to s
                            row=1)

            if T < self.MELT_TEMPERATURE and heat_flag:
                wait_end += self.DELAY_MS
            elif heat_flag: # Should only enter this once
                heat_flag = False
                status = 'Wait'
                self.set_pwm(0)
                self.relay_cool() # safer to keep in this configuration
            
            time.sleep_ms(self.DELAY_MS)
        

    def isothermal(self, filepath, limit, repeat=0):
        '''
        Cool to the temperature denoted by limit as quickly as possible,
        then hold at that temperature.
        '''
        self.screen_put('Isothermal {}'.format(repeat))

        timer = self.timer()
        offset = self.target_pwm(limit)
        overshoot = self.overshoot(limit)

        pid = PI_Controller(self.K_C, self.TAU_I, self.DELAY_S, limit, offset)

        hold_flag = False
        frozen_flag = False
        status = 'Cool' # cool, hold or heat

        self.relay_cool()
        self.set_pwm(100) # Full power
        
        with open(filepath + '/running.csv', 'w') as f:
            t = 0 # Time (ms)
            T, calibrate, ldr = self.read_inputs() # Temperature, temperature, light dependent resistor
            clear_intensity = ldr

            while t < self.MAXIMUM_WAIT and not frozen_flag:
                t = next(timer)
                T, ambient, ldr = self.read_inputs()

                self.screen_put('{} {:5.1f} {:5d}'.format(status,
                                                          T,
                                                          t//1000), # ms to s
                                row=1)

                data = self.csvify(t, T, ambient, ldr, status)
                print(data, end='')
                _ = f.write(data)

                if ldr < clear_intensity - self.LDR_THRESHOLD:
                    frozen_flag = True
                    status = 'Froz'
                    break # Sample is frozen
                
                if not hold_flag: # Haven't reached target temperature yet
                    if T < limit - overshoot:
                        status = 'Hold'
                        hold_start = t
                        hold_flag = True
                else:
                    pwm = pid.proportion(T)
                    self.set_pwm(pwm)
                    
                time.sleep_ms(self.DELAY_MS)# Sleep is bad but can't see an alternative
            else:
                status = 'Warm'

        self.set_pwm(0)
        
        filename = '/{}_isothermal{}_'.format(repeat, limit) # base filename
        if T > 0:
            #  LED has faded meaning false freezes are detected
            os.remove(filepath+'running.csv')
            return False # Gone wrong
        if not hold_flag: #  Sample froze before reaching hold temperature
            filename += 'early_{}'.format(T)
        elif not frozen_flag: # Sample did not freeze within the max wait time
            filename += 'liquid_{}'.format(t)
        else:
            filename += 'frozen_{}'.format(t)
                                         
        filename += '.csv'
        print(filename)
        os.rename(filepath+'/running.csv', filepath+filename)

        self.melt(timer, status)
        return True # Ready for the next isothermal experiment

    def isothermal_experiment(self, filepath, limit):
        repeat = self.get_repeat_number(filepath)
        continue_flag = True

        while continue_flag:
            repeat += 1
            continue_flag = self.isothermal(filepath, limit, repeat)
            
    
    def linear_cool(self, filepath, rate=-1, repeat=0):
        def target_temp(t):
            # Y = mx + c
            return rate * t + fast_cool
        self.screen_put('Linear Cool {}'.format(repeat))
        rate /= 1000 * 60 #  degC/ms
        T, _, ldr = self.read_inputs()

        clear_intensity = ldr

        fast_cool = 0 #  Fast cool to this temperature
        offset = self.target_pwm(fast_cool) # PWM for 0 degrees

        timer = self.timer()
        t = 0
        pid = PI_Controller(self.K_C, self.TAU_I, self.DELAY_S, fast_cool, offset)

        fast_cool_flag = False
        status = 'Fast'
        self.set_pwm(100) # Full power
        with open(filepath+'/running.csv', 'w') as f:
            while T > -25:
                t = next(timer)
                T, T_inner, ldr = self.read_inputs()
                if fast_cool_flag:
                    target_T = target_temp(t)
                    pid.limit = target_T
                    pwm = pid.proportion(T)
                    self.set_pwm(pwm)
                else:
                    if T < fast_cool:
                        status = 'Cool'
                        fast_cool_flag = True
                self.screen_put('{} {:5d} {:5.1f}'.format(status,
                                                          t//1000,
                                                          T), 1)

                if ldr < clear_intensity - self.LDR_THRESHOLD:
                    status = 'Froz'
                    break
                    
                data = self.csvify(t, T, T_inner, ldr)
                _ = f.write(data)
                print(data, end='')

                time.sleep_ms(200)
                
        self.set_pwm(0)

        filename = '/{}_linear{}_'.format(repeat, rate) # base filename
        if T > 0:
            #  LED has faded meaning false freezes are detected
            return False # Gone wrong
        if status != 'Froz': # Sample did not freeze within the ramp
            filename += 'liquid_{}'.format(t)
        else:
            filename += 'frozen_{}'.format(T)
                                         
        filename += '.csv'
        print(filename)
        os.rename(filepath+'/running.csv', filepath+filename)

        self.melt(timer, status)
        return True # Ready for the next isothermal experiment

    def linear_experiment(self, filepath, rate=-1):
        '''Repeatedly linearly cool/thaw at rate degrees/min'''
        
        repeat = self.get_repeat_number(filepath)
        continue_flag = True

        while continue_flag:
            repeat += 1
            continue_flag = self.linear_cool(filepath, rate, repeat)

