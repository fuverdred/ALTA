import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


#====== COLOUR SCHEMES =========================================================
tab10 = [cm.tab10(i) for i in np.linspace(0, 1, 10)]
tab20b = np.array([cm.tab20b(i) for i in np.linspace(0,1,20)]).reshape((5,4,4))

colours = [cm.Set2(i) for i in np.linspace(0,1,8)]
colours2 = [cm.Dark2(i) for i in np.linspace(0,1,8)]
#===============================================================================

#====== LOAD FILES =============================================================
PI_17_files = ['PI_Kc-17_limit-20.csv',
               'PI_Kc-17_limit-15.csv',
               'PI_Kc-17_limit-10.csv']

PI_10_files = ['PI_Kc-10_limit-20.csv',
               'PI_Kc-10_limit-15.csv',
               'PI_Kc-10_limit-10.csv']

PI_5_files = ['PI_Kc-5_limit-20.csv']

thresh_files = ['lab_to_-10.csv',
                'lab_to_-15.csv',
                'lab_to_-20.csv'][::-1]

PI_17 = [np.genfromtxt(f, delimiter=',')[1:] for f in PI_17_files]
PI_10 = [np.genfromtxt(f, delimiter=',')[1:] for f in PI_10_files]
PI_5 =  [np.genfromtxt(f, delimiter=',')[1:] for f in PI_5_files]
limits = (-20, -15,-10) #  3 different temperatures used
thresh = [np.genfromtxt(f, delimiter=',') for f in thresh_files]
#===============================================================================

#====== CLEAN DATA =============================================================
def start_at_zero(data, T_column=2, t_column=0):
    # Set the time at 0 degrees c to 0 minutes
    for i, T in enumerate(data[:,T_column]):
        if T < 0:
            data = data[i:] #  list starts at 0 degrees C
            break
    data[:,t_column] -= data[0][t_column] # set time at start to 0
    data[:,t_column] /= 1000 * 60 # Convert from ms to mins
    return data

PI_17 = [start_at_zero(data) for data in PI_17]
PI_10 = [start_at_zero(data) for data in PI_10]
PI_5 = [start_at_zero(data) for data in PI_5]

thresh = [np.c_[x[:,0], x] for x in thresh] #  Add a column to sub for PWM col
thresh = [start_at_zero(data) for data in thresh]
#===============================================================================


#===== PI Control K_c varied ===================================================
k_values = (-17, -10, -5)
for i, c in enumerate(tab20b[:len(PI_17)]):
    plt.plot((0,12), [limits[i] for _ in (0,12)], 'k--')
    for j, Ks in enumerate((thresh, PI_17, PI_10)):
        plt.plot(Ks[i][:,0], Ks[i][:,2],c=c[j])
        
        plt.xlabel('Time (mins)')
        plt.ylabel('Temperature ($^\circ$C)')
        plt.ylim((-25,0))

plt.show()
