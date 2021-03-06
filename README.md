# ALTA
A version of an Automated Lag-Time Apparatus (ALTA), as described by Baldwin and Vonnegut [Rev. Sci. Instrum. 53, 1911 (1982)] and Barlow and Haymet [Rev. Sci. Instrum. 66, 2966 (1995)]. ALTA repeatedly freeze/thaw cycles a sample of water allowing statistics to be built up on the freezing time/temperature. The process is automated, and can run indefinitely once the sample is inserted.

## Construction

This version uses two Peltier elements for cooling and heating, which sandwich an aluminium block containing the sample. This is shown in the cross section diagram. The aluminium block also contains a platinum resistance thermometer (PRT) and an LED/light dependent resistor (LDR) combination which shines through the sample. When the sample freezes it changes opacity, which is detected by a change in the resistance of the LDR.

<p align="center">
<img src="https://github.com/fuverdred/ALTA/blob/master/images/ALTA_cross_section.svg" alt="ALTA_setup" width="500"/>
</p>

### Electronics

The Peltiers are connected in series across a relay, which allows current to flow in both directions for cooling and heating. Each Peltier is rated at 15.5 V, 4.5 A, powered by a 30 V, 5 A rated power supply they are almost at full power. The power supplied to the Peltier elements is controlled by a pulse width modulated (PWM) MOSFET, at a frequency of 10 kHz. The PWM signal, as well as relay switching and temperature detection are all controlled by a pyBoard 1.1.

<p align="center">
<img src="https://github.com/fuverdred/ALTA/blob/master/images/circuit.png" alt="circuit" width="500"/>
</p>

The above image is the rough circuit board for powering ALTA. Note that some other circuitry is required for the detection of freezing, shown in the schematic below. The board is split in half, with the left dealing with supplying power to the Peltiers also shown in the schematic below, and the right with two voltage step downs (30V -> 10V -> 5V) to allow the fans and pyBoard to all be powered by one supply. This makes ALTA fully self contained, allowing it to be turned on and left alone without having to leave a computer attached to power the pyBoard. The gate drivers ensure the PWM MOSFET is switching quickly, meaning we don't have to heatsink it. The fans switch refers to the fans attached to the heatsinks on the Peltier elements. Using a gate driver on them is overkill, in fact the fans can be left on the whole time if needs be, they are essential while the sample is being cooled, and don't make much difference when the sample is being heated.

The actual implementation of the electronics can be down to the user, this just shows the way I did it (and I'm far from an expert).

<p align="center">
<img src="https://github.com/fuverdred/ALTA/blob/master/images/schematic.png" width="500"/>
</p>

The schematic shows the power circuitry more clearly, along with a voltage divider for measuring the LDR to check if the sample is frozen. The key part of the power circuitry is the inductor and diode for smoothing the PWM. This increases the Peltier's life time. The current set-up of 1mH inductor and diode smooths the current ripple to about 15% of the maximum at full power.

### Temperature Measurements

The temperature is monitored via the PRT built into the aluminium block. The PRT is read by a MAX31865 RTD-to-Digital converter. This is not shown in any of the schematics so far, as it is attached straight to the pyBoard and doesn't require any external power or circuitry. The MAX31865 communicates with the pyBoard via serial peripheral interface (SPI), and the library is included in the software section.

For calibrating the device another PRT is inserted into the sample tube, filled with Ethylene-glycol which has similar thermal properties to water, without the problem of it freezing until much lower temperatures. This allows the small time and temperature lag between the sample and built in PRT to be accounted for, an example is shown in the graph below.

<p align="center">
<img src="https://github.com/fuverdred/ALTA/blob/master/images/calibrate_8.svg" width="500"/>
</p>

### Parts List
- 2x Peltier elements. I would recommend around 4cm x 4cm as this is closer to typical CPU sizes and will make obtaining heat sinks easier. You will also need to consider their maximum power ratings and how you will supply the power.
- 2x Heat sinks. Typical fan assisted CPU heat sinks were able to achieve sub -30°C temperatures, suitable for most ice nucleation experiments.
- Power supply. Peltiers typically require large currents, although the total power consumption  doesn't require specialist equipment. Look at powerful laptop chargers or 3D printer power supplies, which can normally be purchased at a reasonable price.
- Thermal paste.
- LED.
- Light Dependent Resistor.
- Micro-controller of some sort. Any of the many arduinos will work fine, or even a Raspberry Pi, although not with the code in this repository. I think the pyBoard has several key advantages for this project. First it has a REPL meaning you can debug your programs and control ALTA in real time, second it has built in SD card reader so no other peripheral is needed for data storage, third it has built in analog read which Raspberry Pis do not.
- 2x MAX31865 PRT-to-digital converters.
- 2x Platinum resistance thermometers. I used PT100, one in cylindrical form for the aluminium case, and one in surface element form which was submerged in the sample for calibration.
- LCD screen. This can be used to display the current status of ALTA, particularly useful if it is not plugged into a computer.
- Two channel relay module. This will allow heating as well as cooling.
- 1mH Inductor.
- 10V step down converter.
- 5V step down converter. This is to power the micro-controller, not necessary if you will always have a computer plugged into it.
- 1x Power MOSFET. Make doesn't really matter, as long as it is rated for the currents supplied to the Peltier. Of course the schematic will have to change based on whether it is n-type (as here) or p-type.
- Block of aluminium with the same face size as the Peltier coolers. This will need three holes drilled to accomodate the sample, LDR/LED and PRT.
- Insulation. This can be as simple as cutting expanded polystyrene to shape and glueing it to the edges of the aluminium block to keep the temperature low.
- Assorted electrical sundries (resistors, capacitors, diodes, wires...).

The total cost can be as low as £150, a large portion of which depends on the quality of the Peltier elements chosen.

## PyBoard Code
The pyBoard will run any code inside main.py on start-up (right after boot.py, although this can most likely be left alone).

To access the pyBoard REPL:
- Find out what COM port the pyboard is on (Device manager->ports)
- Open a serial communication program such as PuTTY and enter the correct COM port, 115200 Baud

It should open a python REPL with the same scope as main.py, allowing direct interaction with ALTA.

### PyBoard Contents
- boot.py => Leave this alone
- main.py => This will initiate all of the parts of ALTA, and either start an experiment automatically or wait for the user to execute commands via the REPL.
- ALTA.py => This contains the ALTA class, all of the necessary code to run ALTA and collect data from it.
- max31865.py => Library to interface with the MAX31865 RTD-to-digital converter
- max31855.py => Library to interface with the MAX31855 Thermocouple reader. This is a more common chip than the 31865, and could come in useful, although I'd recommend the platinum resistance thermometers for increased stability, precision and accuracy.
- pi_controller.py => Proportional Integral control method for holding a given temperature. Note this is more commonly known as PID control, but the derivative component is not implemented or needed here.
- pyb_i2c_lcd.py => Third party LCD screen library to enable the status to be shown on an LCD display.
- lcd_api.py => Third party LCD screen library


# ALTA.py

This is the main library for ALTA. Here we will briefly go through the constants it contains, the output format of data and the basic functions which can be used. The constants will depend on your particular set up, so we will also look at some of the calibration functions which are implemented, although I would recommend extensive testing to find what is best.

## INPUTS & OUTPUTS

Inputs:
1. Aluminium body temperature from a platinum resistance thermometer drilled
into the aluminium just below the sample vial.
2. Calibration platinum resistance thermometer placed in the sample container.
3. A light dependent resistor (LDR) value which dictataes whether or not
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


