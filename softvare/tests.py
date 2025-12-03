# main_yolo_arduino.py
import cv2
import serial
import time

from testScript import YoloDetector

PORT = "dev/ttyACM0"      # поменяй на свой при необходимости
BAUD = 115200


def main():
    # ---------- ОТКРЫВАЕМ SERIAL ----------
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[PC] Открыт порт {PORT} со скоростью {BAUD}")

    # даём Arduino перезагрузиться
    time.sleep(2)

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # ---------- ОТКРЫВАЕМ КАМЕРУ ----------
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        ser.close()
        raise RuntimeError("Камера не открылась")

    # ---------- ЗАГРУЖАЕМ МОДЕЛЬ ----------
    detector = YoloDetector(device="cpu")  # или "cuda", если есть GPU

    prev_in_focus = False  # состояние "объект по центру" на прошлом кадре

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[PC] Не удалось прочитать кадр")
                break

            # Детектируем объект
            in_focus, vis = detector.detect_centered(frame, draw=True)

            # Логика:
            #   если в прошлом кадре НЕ было по центру, а сейчас ЕСТЬ → фронт сигнала
            #   посылаем "start" ОДИН раз
            if in_focus and not prev_in_focus:
                ser.write(b"start\n")
                ser.flush()
                print("[PC] Sent: start (объект по центру)")

            prev_in_focus = in_focus

            # Показ кадра (для отладки)
            #cv2.imshow("YOLO + Arduino", vis)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        ser.close()
        print("[PC] Порт закрыт, камера освобождена")


if __name__ == "__main__":
    main()