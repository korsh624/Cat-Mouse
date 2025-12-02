import cv2
import numpy as np
import serial
import time
PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
TIMEOUT = 1
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
print("Порт открыт")
time.sleep(2)

cap = cv2.VideoCapture(0)  # при необходимости поменяй индекс/URL

if not cap.isOpened():
    raise RuntimeError("Kamera ne otkrylas'")

min_area = 500

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Ne udalos' prochitat' kadr")
            break

        # размер кадра (g_y – высота, g_x – ширина)
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

        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(c)
            #print("bounding box:", x, y)

            # центр объекта по X
            center_x_obj = x + w // 2
            # разница между центром объекта и центром кадра
            dx = center_x_obj - center_x_frame

            # рисуем зелёный прямоугольник вокруг красного объекта
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # центр кадра (красный круг)
            cv2.circle(output, (g_x // 2, g_y // 2), 10, (0, 0, 255), 2)
            # центр объекта (синий круг)
            cv2.circle(output, (center_x_obj, y + h // 2), 10, (255, 0, 0), 2)

            # Пишем в терминал ТОЛЬКО если dx в диапазоне [-50, 50]
            if -50 <= dx <= 50:
                print(f"vizhu, dx={dx}")
                ser.write(b'start\n')
                ser.flush()
                print('sendet to arduinio')

        # --- ВЫВОД ИЗОБРАЖЕНИЯ ---
        cv2.imshow("frame", output)  # кадр с прямоугольниками
        cv2.imshow("mask", mask)     # бинарная маска красного

        # Выход по клавише 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Ostanovleno pol'zovatelem")
finally:
    cap.release()
    cv2.destroyAllWindows()