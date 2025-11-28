import serial
import time

# Настройки Serial-порта
PORT = 'COM3'        # Замените на ваш порт (например, '/dev/ttyUSB0' в Linux)
BAUD_RATE = 115200     # Скорость обмена (должна совпадать с Arduino)
TIMEOUT = 1          # Таймаут чтения (сек)

def send_start_command():
    try:
        # Открываем Serial-порт
        ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"Подключено к {PORT} на скорости {BAUD_RATE} бод")

        # Ждём 2 секунды, чтобы Arduino инициализировался
        time.sleep(2)

        # Отправляем команду 'start' + перевод строки (как в Serial Monitor)
        ser.write(b'stop')
        print("Команда 'start' отправлена")
        ser.close()
        print("Порт закрыт")

    except serial.SerialException as e:
        print(f"Ошибка Serial: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == '__main__':
    send_start_command()
