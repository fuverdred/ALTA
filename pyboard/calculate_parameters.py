'''
Work out tuning correlations for PID control
'''

#These are all worked out from a first order + dead time fitting function
K_p = -0.42
tau_p = 124.0
theta_p = 5.0

tau_c_aggressive = max([0.1*tau_p, 0.8*theta_p])
tau_c_moderate = max([tau_p, 8*theta_p])
tau_c_conservative = max([10*tau_p, 80*theta_p])

tau_c = tau_c_aggressive

K_c = (tau_p + 0.5*theta_p)/(K_p*(tau_c + 0.5*theta_p))
tau_I = tau_p + 0.5*theta_p
tau_D = (tau_p * theta_p)/(2*tau_p + theta_p)

#derivataive filter
alpha = (tau_c*(tau_p + 0.5* theta_p))/(tau_p*(tau_c+theta_p))

print(f'K_c : {K_c}\n'
      f'tau_I: {tau_I}\n'
      f'tau_D: {tau_D}\n'
      f'alpha: {alpha}')
