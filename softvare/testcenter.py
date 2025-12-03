import cv2
import numpy as np
import serial
import time

PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
TIMEOUT = 1

# таймаут на запись, чтобы не вешаться при проблемах с портом
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT, write_timeout=0.2)
print("Порт открыт")
time.sleep(2)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Камера не открылась")

min_area = 500
sent_start = False  # уже отправляли команду "start" или нет

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось прочитать кадр")
            break

        g_y, g_x = frame.shape[:2]
        center_x_frame = g_x // 2  # центр кадра по X

        # --- Обработка кадра ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        output = frame.copy()

        # рисуем центр кадра (красный круг)
        cv2.circle(output, (center_x_frame, g_y // 2), 10, (0, 0, 255), 2)

        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(c)

            # центр объекта по X
            center_x_obj = x + w // 2
            dx = center_x_obj - center_x_frame

            # рисуем зелёный прямоугольник и синий центр объекта
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(output, (center_x_obj, y + h // 2), 10, (255, 0, 0), 2)

            # Отправляем "start" ТОЛЬКО ОДИН РАЗ, когда объект в центре
            if -50 <= dx <= 50 and not sent_start:
                print(f"вижу, dx={dx}")
                try:
                    ser.write(b"start\n")
                    print("отправлено на Arduino")
                    sent_start = True
                except serial.SerialTimeoutException:
                    print("Таймаут записи в порт")
                except serial.SerialException as e:
                    print("Ошибка порта:", e)

        # --- ВЫВОД ИЗОБРАЖЕНИЯ ---
        cv2.imshow("frame", output)
        cv2.imshow("mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        # по желанию: сбросить флаг отправки по клавише 'r'
        if key == ord('r'):
            sent_start = False
            print("Флаг отправки сброшен")

except KeyboardInterrupt:
    print("Остановлено пользователем")
finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()