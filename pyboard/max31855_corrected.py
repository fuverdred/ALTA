import ustruct

class MAX31855():
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs # chip select
        self.data = bytearray(4)

    def read(self, internal=False, voltage=False):
        '''
        Read the output buffer of the thermocouple. Returns a list of
        values [temp, internal_temp, voltage] Optional flags:
        internal: Also return the internal temperature of the device
        voltage : Also return the raw voltage of the junction
        '''
        data = bytearray(4)
        try:
            self.cs.low()
            self.spi.recv(data)
        finally:
            self.cs.high()

        #Unpack into two signed shorts (two bytes each, big endian)
        temperature, reference = ustruct.unpack('>hh', data)

        if reference & 0b1:
            print('Thermocouple not connected') #  OC Fault
            return None
        if reference & 0b10:
            print('Thermocouple shorted to ground') #  SCG Fault
            return None
        if reference & 0b100:
            print('Thermocouple shorted to Vcc') #  SCV Fault
            return None

        internal_temperature = (reference >> 4) * 0.0625

        if temperature & 0x01:
            print("Error has occurred") #  Should be dealt with before
        temperature = [(temperature >> 2)/4] # Get rid of first 2 bits leaving 14 bit Temperature

        voltage = (temperature - internal_temperature) * 0.041276

        if internal:
            temperature.append(internal_temperature)
        if voltage:
            temperature.append(voltage)

        return temperature
        
