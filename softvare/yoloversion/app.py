from flask import Flask, Response, render_template, request
import cv2
import threading
import time
import atexit
from eval import findSquare
print('start app ')
app = Flask(__name__)

# Параметры камеры: можно заменить 0 на путь к RTSP или файл
CAMERA_SOURCE = 0

class Camera:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        # Настройки по желанию
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        # Запускаем поток захвата
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            d,frame=findSquare(frame)

            if not ret:
                # небольшая пауза при проблеме с чтением
                time.sleep(0.1)
                continue
            # Здесь можно делать обработку кадра (детекция, рисование bbox и т.д.)
            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            # Возвращаем копию, чтобы избежать гонок
            return self.frame.copy()

    def stop(self):
        self.running = False
        # дождаться завершения потока
        self.thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()

camera = Camera(CAMERA_SOURCE)

# Гарантированно освобождаем камеру при завершении приложения
def cleanup():
    camera.stop()

atexit.register(cleanup)

def encode_frame(frame, jpeg_quality=80):
    # Кодируем в JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    ret, jpeg = cv2.imencode('.jpg', frame, encode_param)
    if not ret:
        return None
    return jpeg.tobytes()

def frame_generator():
    """Генератор кадров для MJPEG-потока."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            # если кадра пока нет, подождём немного
            time.sleep(0.05)
            continue
        # (опционально) преобразования, конвертация цветов
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        jpg = encode_frame(frame, jpeg_quality=80)
        if jpg is None:
            continue

        # Формируем multipart сообщение для MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
        # Можно регулировать fps:
        time.sleep(0.03)  # ~30 FPS максимум (в реале зависит от захвата и сети)

@app.route('/')
def index():
    # Простейшая страница с видеоплеером
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Возвращаем ответ с правильным MIME-типом для MJPEG
    return Response(frame_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Можно изменить host/port или задать debug=True в разработке
    app.run(host='0.0.0.0', port=5000, threaded=True)