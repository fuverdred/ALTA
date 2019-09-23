# ALTA
A version of an Automated Lag Time Apparatus, as described by Baldwin and Vonnegut [Rev. Sci. Instrum. 53, 1911 (1982)] and Barlow and Haymet [Rev. Sci. Instrum. 66, 2966 (1995)]

This version uses two Peltier elements for cooling and heating. The cold sides sandwich an aluminium block which has several holes drilled in it for a sample, platinum resistance thermometer, LED and LDR. There is a heat sink with fan on each hot side, with bolts to hold the whole setup together.

The Peltiers are connected in series across a relay, which allows current to flow in both directions for cooling and heating. Each Peltier is rated at 15.5V, 4.5A, however the current power supply is limited to 20V (providing ~3A). The power supplied to the Peltier elements is controlled by a pulse width modulated (PWM) MOSFET, at a frequency of 1kHz. The PWM signal, as well as relay switching and temperature detection are all controlled by a pyBoard 1.0

![ALTA_setup](https://github.com/fuverdred/ALTA/blob/master/images/ALTA.jpg)

## Temperature Measurements
For experiments a platinum resistance thermometer (PT100) is situated just under the bottom of the sample tube. This quickly and reliably tells the temperature to a precision of 0.1K. For calibrating the device a K-type thermocouple is also used. This can be inserted into the sample tube, filled with Ethylene-glycol which has similar thermal properties to water, without the problem of it freezing until much lower temperatures. This shows the small time and temperature lag between the sample and PT100, which must be accounted for.
