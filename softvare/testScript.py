import os
os.environ["OPENCV_VIDEOIO_PRIORITY_GSTREAMER"] = "0"

import time
import serial
import cv2
from flask import Flask, Response, render_template_string

PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
TIMEOUT = 1


def send_start():
    ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    print("Порт открыт")
    time.sleep(2)
    ser.write(b'start\n')
    ser.flush()
    print("Команда start отправлена")
    ser.close()
    print("Порт закрыт")


app = Flask(__name__)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("Не удалось открыть камеру")
else:
    print("Камера успешно открыта")


def gen_frames():
    while True:
        if not cap.isOpened():
            print("Камера закрыта, выходим из gen_frames")
            break

        success, frame = cap.read()
        if not success:
            print("Не удалось получить кадр с камеры")
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )


@app.route('/video')
def video():
    return Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/')
def index():
    html = '''
    !DOCTYPE html
    html
    head
      meta charset="utf-8"
      titleТест: робот + камера/title
      style
        body  font-family: sans-serif; background: f0f0f0; 
        .container  max-width: 900px; margin: 20px auto; background: fff;
                     padding: 20px; border-radius: 8px; 
        img  width: 100%; max-width: 800px; border: 1px solid ccc; 
      /style
    /head
    body
      div class="container"
        h1Тест: робот + видеопоток/h1
        pПри запуске скрипта роботу отправлена команда codestart/code./p
        img src=" url_for(video) " alt="Video stream"
      /div
    /body
    /html
    '''
    return render_template_string(html)


if __name__ == "__main__":
    send_start()
    try:
        print("Запускаем Flask на 0.0.0.0:8080")
        app.run(host="0.0.0.0", port=8080, threaded=False)
    finally:
        print("Остановка приложения")
        if cap is not None and cap.isOpened():
            cap.release()
            print("Камера закрыта")
