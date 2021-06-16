# ALTA
A version of an Automated Lag-Time Apparatus (ALTA), as described by Baldwin and Vonnegut [Rev. Sci. Instrum. 53, 1911 (1982)] and Barlow and Haymet [Rev. Sci. Instrum. 66, 2966 (1995)]. ALTA repeatedly freeze/thaw cycles a sample of water allowing statistics to be built up on the freezing time/temperature. The process is automated, and can run indefinitely once the sample is inserted.

## Construction

This version uses two Peltier elements for cooling and heating, which sandwich an aluminium block containing the sample. This is shown in the cross section diagram. The aluminium block also contains a platinum resistance thermometer (PRT) and an LED/light dependent resistor (LDR) combination which shines through the sample. When the sample freezes it changes opacity, which is detected by a change in the resistance of the LDR.

![ALTA_setup](https://github.com/fuverdred/ALTA/blob/master/images/ALTA_cross_section.svg)

### Electronics

The Peltiers are connected in series across a relay, which allows current to flow in both directions for cooling and heating. Each Peltier is rated at 15.5 V, 4.5 A, powered by a 30 V, 5 A rated power supply they are almost at full power. The power supplied to the Peltier elements is controlled by a pulse width modulated (PWM) MOSFET, at a frequency of 10 kHz. The PWM signal, as well as relay switching and temperature detection are all controlled by a pyBoard 1.1.

![power_circuit](https://github.com/fuverdred/ALTA/blob/master/images/circuit.png)

The above image is the rough circuit board for powering ALTA. Note that some other circuitry is required for the detection of freezing, shown in the schematic below. The board is split in half, with the left dealing with supplying power to the Peltiers, and the right with two voltage step downs (30V -> 10V -> 5V) to allow the fans and pyBoard to all be powered by one supply.

![schematic](https://github.com/fuverdred/ALTA/blob/master/images/schematic.png)

## Temperature Measurements
For experiments a platinum resistance thermometer (PRT) (PT100) is situated just under the bottom of the sample tube. This quickly and reliably tells the temperature to a precision of 0.1K. For calibrating the device another PRT is inserted into the sample tube, filled with Ethylene-glycol which has similar thermal properties to water, without the problem of it freezing until much lower temperatures. This shows the small time and temperature lag between the sample and built in PRT, which must be accounted for.

## PyBoard Code
The pyBoard will run any code inside main.py. Currently it initiates all of the methods of interaction with ALTA:
- Built in PRT
- Sample PRT
- Light dependent resistor (LDR) read via analogue read
- Fans pin, standard IO pin

It also creates an instance of the ALTA class, which has methods for running ice nucleation experiments.

To interact with the pyboard via serial:
- Find out what COM port the pyboard is on (Device manager->ports)
- Open a serial communication program such as PuTTY and enter the correct COM port, 115200 Baud

It should open a python REPL with the same scope as main.py, allowing direct interaction with ALTA.
