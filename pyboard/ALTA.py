import time
import urandom
from pyb import SPI, Pin, millis, Timer

from MAX31865 import MAX31865
from MAX31855 import MAX31855


class ALTA():
    def __init__(self, ptd, k, pwm_channel, relay_1, relay_2):
        self.ptd = ptd
        self.k = k
        self.pwm_channel = pwm_channel
        self.relay_1 = relay_1
        self.relay_2 = relay_2
        self.relay_1(True) #  off
        self.relay_2(True) #  off

        self.set_point = -15
        self.pw = 0 #  MOSFET off
        self.T = self.ptd.read() #  deg C
        self.delay = 200 #  ms
        self.start = millis()
        self.t = self.start
        
        self.K_c = -8.0
        self.tau_I = 126
        self.tau_D = 2.5
        self.alpha = 1.0
        self.I = 0


    def proportion(self):
        e = self.set_point - self.T
        
        P = self.K_c * e
        
        self.I += e * (self.delay/1000)
        I = (self.K_c/self.tau_I) * self.I

        D = -1 * self.K_c * self.tau_D * (self.T-self.last_T)/self.delay
        self.last_T = self.T 
        
        PID = P + I + D
        if PID > 100:
            return 100 #  100 is the maximum value
        if PID < 0:
            return 0
        return int(PID)

    def loop_to_target(self, set_point):
        filename = 'PID_Kc'+str(self.K_c)+'_limit'+str(set_point)+'.csv'
        self.f = open('data/'+filename, 'w')

        self.I = 0 #  resest PID control
        
        self.set_point = set_point
        self.T = self.ptd.read()
        if self.T > self.set_point:
            self.relay_1(False) #  Cooling mode

        self.I = 0 #  resest PID control
        self.last_T = self.T #  for calculating derivative
        
        self.start = millis()
        self.t = self.start

        while self.t < self.start + 300 * 1e3:
            self.T = self.ptd.read()
            self.T_k = self.k.read()[0]
            self.t = millis() - self.start
            self.pw = self.proportion()
            self.pwm_channel.pulse_width_percent(self.pw)

            print(self.t, self.pw, self.T, self.T_k)
            self.f.write(','.join([str(i) for i in (self.t,
                                                self.pw,
                                                self.T,
                                                self.T_k)]) + '\n')
            time.sleep_ms(self.delay)
            
        self.f.close()
        self.pwm_channel.pulse_width_percent(0)
        self.relay_1(True)

    def fast_loop(self, set_point):
        filename = 'fix_fast_cool_to_'+str(set_point)+'_Kc_'+str(self.K_c)+'.csv'
        self.f = open('data/'+filename, 'w')

        self.set_point = set_point
        self.T = self.ptd.read()

        self.I = 0
        self.last_T = self.T

        self.start = millis()
        self.t = self.start

        self.relay_1(False) #  Cooling mode
        self.pw = 100
        self.pwm_channel.pulse_width_percent(self.pw) # Full gas cooling

        while self.T > self.set_point + 0.5:
            #Cool as quickly as possible to the limit in this loop
            self.T = self.ptd.read()
            self.T_k = self.k.read()[0]
            self.t = millis() - self.start
            _ = self.proportion() #  Start adding up the integral contribution

            print(self.t, self.pw, self.T, self.T_k)
            self.f.write(','.join([str(i) for i in (self.t,
                                                self.pw,
                                                self.T,
                                                self.T_k)]) + '\n')
            time.sleep_ms(self.delay)
            self.last_T = self.T #  For when D in PID starts


        while self.t < (500*1000):
            #Hold the temp constant with PWM
            self.T = self.ptd.read()
            self.T_k = self.k.read()[0]
            self.t = millis() - self.start

            self.pw = self.proportion()
            self.pwm_channel.pulse_width_percent(self.pw)
            

            print(self.t, self.pw, self.T, self.T_k)
            self.f.write(','.join([str(i) for i in (self.t,
                                                self.pw,
                                                self.T,
                                                self.T_k)]) + '\n')
            time.sleep_ms(self.delay)

        self.f.close()
        self.relay_1(True)
        self.pwm_channel.pulse_width_percent(0)

    def linear_cool(self, rate_min):
        def target_T(t):
            return rate * t + initial_T

        min_in_ms = 60 * 1000
        rate = rate_min / min_in_ms # degc / ms

        initial_T = self.ptd.read()
        initial_t = millis()

        self.relay_1(False)
        self.t = initial_t
        self.T = initial_T

        self.last_T = self.T

        filename = 'linear_cool_Kc'+str(self.K_c)+'_rate'+str(rate_min)+'.csv'
        self.f = open('data/'+filename, 'w')

        while self.T > -20:
            self.t = millis() - initial_t
            self.T = self.ptd.read()
            self.T_k = self.k.read()[0]
            self.set_point = target_T(self.t)
            self.pw = self.proportion()
            self.pwm_channel.pulse_width_percent(self.pw)
            
            print(self.t, self.pw, self.T, self.T_k)
            self.f.write(','.join([str(i) for i in (self.t,
                                                self.pw,
                                                self.T,
                                                self.T_k)]) + '\n')
            time.sleep_ms(self.delay)

        self.f.close()
        self.relay_1(True)
        self.pwm_channel.pulse_width_percent(0)
            

        

            
            
