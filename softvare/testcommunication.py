import serial
import time

# замените COM3 на свой порт, например COM4, /dev/ttyUSB0 и т.д.
ser = serial.Serial("COM4", 115200, timeout=1)

time.sleep(2)  # дать Arduino перезагрузиться
input()
ser.write(b"start\n")    # отправляем команду включить LED
print("Sent: start")



ser.close()
