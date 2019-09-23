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
        self.delay = 100 #  ms
        self.start = millis()
        self.t = self.start
        
        self.K_c = -10
        self.tau_I = 124
        self.I = 0


    def proportion(self):
        e = self.set_point - self.T
        P = self.K_c * e
        self.I += e * (self.delay/1000)
        I = (self.K_c/self.tau_I) * self.I
        PI = P + I
        if PI > 100:
            return 100 #  100 is the maximum value
        if PI < 0:
            return 0
        return PI

    def loop_to_target(self, set_point):
        filename = 'PI_Kc'+str(self.K_c)+'_limit'+str(set_point)+'.csv'
        self.f = open('data/'+filename, 'w')

        self.I = 0 #  resest PID control
        
        self.set_point = set_point
        self.T = self.ptd.read()
        if self.T > self.set_point:
            self.relay_1(False) #  Cooling mode
        self.start = millis()
        self.t = self.start

        while self.t < self.start + 600 * 1e3:
            self.T = self.ptd.read()
            self.T_k = self.k.read()
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

    def linear_cool(self):
        def target_T(t):
            return rate * t + initial_T
            
        min_in_ms = 60 * 1000
        rate = -1 / min_in_ms # degc / ms

        initial_T = self.ptd.read()
        initial_t = millis()

        self.relay_1(False)
        self.t = initial_t
        self.T = initial_T

        filename = 'linear_cool_Kc'+str(self.K_c)+'.csv'
        self.f = open('data/'+filename, 'w')

        while self.t < initial_t + 1000 * 60 *5:
            self.t = millis() - initial_t
            self.T = self.ptd.read()
            self.T_k = self.k.read()
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
            

        

            
            
