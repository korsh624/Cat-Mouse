from ultralytics import YOLO
import cv2
# Загрузка обученной модели
model = YOLO("best1.pt")  # путь к вашим весам
x_center=0
y_center=0
def findSquare(frame):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    frame=cv2.resize(frame, (640,480))
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
                cv2.circle(frame, (int(frame_width//2), int(frame_height//2)), 5, (255, 0, 0), cv2.FILLED)
                dx=abs(x_center-frame_width//2)
                if dx < 50:
                    print('in focus')
                    return True, frame
        # cv2.imshow("YOLO Robot Detection", frame)
        if cv2.waitKey(1) == ord('q'):
            exit()
    return False, frame
