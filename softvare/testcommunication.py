import serial
import time

PORT = "COM17"      # замени на свой порт
BAUD = 115200


def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[PC] Открыт порт {PORT} со скоростью {BAUD}")

    # Дать Arduino перезагрузиться
    time.sleep(2)

    # Очистить буферы от мусора
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print("[PC] Готов отправлять команды. Каждое нажатие Enter = команда 'start'.")

    for i in range(1, 4):
        input(f"[PC] Нажми Enter для отправки команды start #{i}...")
        ser.write(b"start\n")
        ser.flush()
        print(f"[PC] Отправлено: start #{i}")

        # подождём чуть-чуть, чтобы Arduino успел что-то ответить
        time.sleep(0.2)
        while ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print("[PC] От Arduino:", line)

    print("[PC] Ждём ещё немного, пока Arduino допечатает...")
    time.sleep(2)
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print("[PC] От Arduino:", line)

    ser.close()
    print("[PC] Порт закрыт")


if __name__ == "__main__":
    main()
