class PI_Controller():
    '''
    Proportional - Integral controller to maintain the target temperature.
    K_c: Feedback constant
    tau_I: Integral time constant
    delta_t: Time step between readings (s)
    limit: Target temperature (deg C)
    offset: Initial value for the PI controller to return
    '''
    def __init__(self, K_c, tau_I, delta_t, limit, offset=0):
        self.limit = limit # Degrees C
        self.offset = offset
        self.K_c = K_c
        self.tau_I = tau_I
        self.delta_t = delta_t # Seconds
   
        self.I = 0 #  Current integral value

    def reset(self):
        self.I = 0

    def proportion(self, temperature, components=False):
        error = self.limit - temperature

        P = error * self.K_c

        self.I += error * self.delta_t
        I = (self.K_c / self.tau_I) * self.I

        PI = P + I + self.offset

        if components:
            return PI, P , I
        return PI
