import cv2
import serial
import time
import torch
import pathlib

# ---------- ПАТЧ ДЛЯ WINDOWS WEIGHTS НА LINUX ----------
# Если в .pt внутри есть WindowsPath, подменяем его на PosixPath,
# чтобы torch.load мог его распаковать.
pathlib.WindowsPath = pathlib.PosixPath
# -------------------------------------------------------

# --------- НАСТРОЙКИ ---------
PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
TIMEOUT = 1

MODEL_PATH = "best.pt"          # путь к твоей модели YOLOv5
TARGET_CLASS_NAME = "figure"    # имя класса из обучения
CONF_THRESH = 0.5               # порог уверенности
CENTER_TOLERANCE = 50           # допуск по центру [-50, 50] пикселей
MIN_AREA = 500                  # минимальная площадь бокса
# -----------------------------

# Открываем Serial
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT, write_timeout=0.2)
print("Порт открыт")
time.sleep(2)

# Загружаем модель YOLOv5
model = torch.hub.load(
    'ultralytics/yolov5',
    'custom',
    path=MODEL_PATH,
    source='github',
    device='cpu'          # можно 'cuda' если есть GPU
    # , force_reload=True  # можно добавить, если будет ругаться на кэш
)
model.conf = CONF_THRESH

print("Модель загружена:", MODEL_PATH)
print("Классы модели:", model.names)

# Камера
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Камера не открылась")

sent_start = False  # уже отправляли "start" или нет

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось прочитать кадр")
            break

        g_y, g_x = frame.shape[:2]
        center_x_frame = g_x // 2

        output = frame.copy()
        cv2.circle(output, (center_x_frame, g_y // 2), 10, (0, 0, 255), 2)

        # --------- ДЕТЕКЦИЯ YOLOv5 ---------
        results = model(frame, size=640)
        # results.xyxy[0]: [x1, y1, x2, y2, conf, cls]
        preds = results.xyxy[0].cpu().numpy()

        for *xyxy, conf, cls_id in preds:
            x1, y1, x2, y2 = map(int, xyxy)
            w = x2 - x1
            h = y2 - y1
            area = w * h
            if area < MIN_AREA:
                continue

            cls_id = int(cls_id)
            cls_name = model.names[cls_id]

            if cls_name != TARGET_CLASS_NAME:
                continue

            center_x_obj = x1 + w // 2
            center_y_obj = y1 + h // 2
            dx = center_x_obj - center_x_frame

            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(output, (center_x_obj, center_y_obj), 10, (255, 0, 0), 2)
            cv2.putText(output, f"{cls_name} {conf:.2f}",
                        (x1, max(0, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # ---------- ОТПРАВКА КОМАНДЫ В ARDUINO ----------
            if -CENTER_TOLERANCE <= dx <= CENTER_TOLERANCE and not sent_start:
                print(f"Вижу {cls_name} по центру, dx={dx}")
                try:
                    ser.write(b"start\n")
                    print("Отправлено на Arduino")
                    sent_start = True
                except serial.SerialException as e:
                    print("Ошибка записи в порт:", e)

        # --------- ПОКАЗ КАДРА ---------
        cv2.imshow("frame", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('r'):
            sent_start = False
            print("Флаг отправки сброшен")

except KeyboardInterrupt:
    print("Остановлено пользователем")
finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()