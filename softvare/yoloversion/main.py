# main_yolo_arduino.py
import cv2
import serial
import time
import eval as detector
from app import app
PORT = "/dev/ttyACM0"      # поменяй на свой при необходимости
BAUD = 115200
def main():
    ser = serial.Serial(PORT, BAUD)
    print(f"[PC] Открыт порт {PORT} со скоростью {BAUD}")
    time.sleep(2)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    prev_in_focus = False

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    in_focus=False
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[PC] Не удалось прочитать кадр")
                break
            in_focus, vis = detector.findSquare(frame)
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
    # app.run(host='0.0.0.0', port=5000, threaded=True)
