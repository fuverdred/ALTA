import time
import MAX31865

rtd = MAX31865()
while True:
    temp = rtd.read()
    print(temp)
    time.sleep(5)
