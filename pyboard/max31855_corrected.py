import ustruct

class MAX31855():
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs # chip select
        self.data = bytearray(4)

    def read(self):
        data = bytearray(4)
        try:
            self.cs.low()
            self.spi.recv(data)
        finally:
            self.cs.high()

        #Unpack into two signed shorts (two bytes each, big endian)
        temperature, reference = ustruct.unpack('>hh', data)

        if reference & 0b111:
            print("Some sort of error as occurred, soz")
            #This should be expanded for the first 3 bits which have
            #specific errors

        internal_temperature = reference >> 4

        if temperature & 0x01:
            print("Some sort of error has occurred, soz")
        temperature >>= 2 # Get rid of first 2 bits leaving 14 bit Temperature

        voltage = (temperature - internal_temperature) * 0.041276

        return temperature, reference_temperature, voltage
        
