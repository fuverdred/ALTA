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

        if temperature & 0x01:
            print("Some sort of error has occurred, soz")
        return (temperature >> 2)/4
