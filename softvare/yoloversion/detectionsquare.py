from ultralytics import YOLO
import cv2
# Загрузка обученной модели
model = YOLO("best1.pt")  # путь к вашим весам
x_center=0
y_center=0
# Открываем видео
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('output.mp4')


# Проверяем, открылось ли видео
if not cap.isOpened():
    print("Ошибка: Не удалось открыть видео!")
    exit()

# Читаем видео и обрабатываем каждый кадр
while True:
    cropped_img = 0
    ret, frame = cap.read()
    frame=cv2.resize(frame, (640,480))
    # cv2.line(frame, (410, 0), (410, 480), (0, 0, 255), thickness=3)
    # cv2.line(frame, (0, 240), (640, 240), (0, 0, 255), thickness=3)
    if not ret:
        break  # видео закончилось
    results = model.predict(frame, conf=0.7)  # conf - порог уверенности
    for result in results:
        if result.boxes:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # координаты bbox
                cropped_img = frame[y1:y1 + y2, x1:x1 + x2]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                x_center=x1+(x2-x1)//2
                y_center = y1+(y2 - y1) // 2
                cv2.circle(frame, (int(x_center), int(y_center)), 5, (0, 0, 255), cv2.FILLED)

                # cv2.imshow("Robot Detection", cropped_img)
    # cv2.imshow("YOLO Robot Detection", frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()