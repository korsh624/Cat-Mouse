# detector.py
import cv2
import torch
import pathlib

# Патч для весов, сохранённых под Windows, чтобы они грузились в Linux
pathlib.WindowsPath = pathlib.PosixPath

# --------- НАСТРОЙКИ МОДЕЛИ ---------
MODEL_PATH = "best.pt"          # путь к твоей модели YOLOv5
TARGET_CLASS_NAME = "figure"    # имя класса из обучения
CONF_THRESH = 0.5               # порог уверенности
CENTER_TOLERANCE = 50           # допуск по центру [-50, 50] пикселей
MIN_AREA = 500                  # минимальная площадь бокса
# -----------------------------------


class YoloDetector:
    def __init__(self,
                 model_path: str = MODEL_PATH,
                 target_class: str = TARGET_CLASS_NAME,
                 conf_thresh: float = CONF_THRESH,
                 center_tolerance: int = CENTER_TOLERANCE,
                 min_area: int = MIN_AREA,
                 device: str = "cpu"):
        """
        Загружает модель YOLOv5 и сохраняет параметры.
        device: 'cpu' или 'cuda'
        """
        self.target_class = target_class
        self.center_tolerance = center_tolerance
        self.min_area = min_area

        self.model = torch.hub.load(
            'ultralytics/yolov5',
            'custom',
            path=model_path,
            source='github',
            device=device
        )
        self.model.conf = conf_thresh

        print("YOLO-модель загружена из:", model_path)
        print("Классы модели:", self.model.names)

    def detect_centered(self, frame, draw: bool = True):
        """
        На вход: кадр (BGR, как из OpenCV).
        На выход:
          - in_focus: bool — есть ли целевой объект в центре
          - output: кадр с нарисованными боксами (если draw=True)
        """
        h, w = frame.shape[:2]
        center_x_frame = w // 2

        output = frame.copy()

        # Запуск модели
        results = self.model(frame, size=640)
        preds = results.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, cls]

        in_focus = False

        for *xyxy, conf, cls_id in preds:
            x1, y1, x2, y2 = map(int, xyxy)
            bw = x2 - x1
            bh = y2 - y1
            area = bw * bh
            if area < self.min_area:
                continue

            cls_id = int(cls_id)
            cls_name = self.model.names[cls_id]

            if cls_name != self.target_class:
                continue

            center_x_obj = x1 + bw // 2
            center_y_obj = y1 + bh // 2
            dx = center_x_obj - center_x_frame

            if draw:
                # цвет бокса: красный, если по центру, зелёный — если нет
                color = (0, 255, 0)
                if -self.center_tolerance <= dx <= self.center_tolerance:
                    color = (0, 0, 255)

                cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
                cv2.circle(output, (center_x_obj, center_y_obj), 5, (255, 0, 0), 2)
                cv2.putText(output, f"{cls_name} {conf:.2f}",
                            (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Условие "объект по центру"
            if -self.center_tolerance <= dx <= self.center_tolerance:
                in_focus = True

        if draw:
            # рисуем центр кадра
            cv2.circle(output, (center_x_frame, h // 2), 5, (0, 255, 255), 2)

        return in_focus, output