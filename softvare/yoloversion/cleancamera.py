# camera_utils.py
import cv2
import os
import subprocess
import time
import signal


def force_release_camera():
    """Принудительно освободить камеру от всех процессов"""
    try:
        # Закрываем все процессы, использующие видеоустройства
        for i in range(10):
            video_device = f"/dev/video{i}"
            if os.path.exists(video_device):
                try:
                    # Находим и убиваем процессы, использующие камеру
                    result = subprocess.run(
                        ['fuser', video_device],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        pids = result.stdout.strip().split()
                        for pid in pids:
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"Процесс {pid} завершен")
                            except:
                                pass
                except:
                    pass

        # Дополнительно: сбрасываем USB порт (если камера USB)
        try:
            # Найти USB порт камеры Orbbec
            subprocess.run(['usbreset', '2bc5:0636'], check=False)
        except:
            pass

        # Небольшая задержка для освобождения ресурсов
        time.sleep(1)

    except Exception as e:
        print(f"Ошибка при освобождении камеры: {e}")


def safe_camera_open(camera_index=0, timeout=10):
    """Безопасное открытие камеры с очисткой предыдущих подключений"""

    force_release_camera()

    # Пробуем разные индексы и пути
    sources_to_try = [
        camera_index,
        10,  # Часто для Orbbec
        1, 2, 3, 4,
        '/dev/video0',
        '/dev/video1',
        '/dev/video2',
        '/dev/video4',
        '/dev/video10'
    ]

    cap = None
    found_source = None

    for source in sources_to_try:
        print(f"Пробуем открыть камеру: {source}")
        try:
            if isinstance(source, int):
                cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
            else:
                cap = cv2.VideoCapture(source, cv2.CAP_V4L2)

            if cap.isOpened():
                # Проверяем, можем ли прочитать кадр
                for _ in range(5):  # Пробуем несколько раз
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        found_source = source
                        print(f"Камера успешно открыта: {source}")

                        # Настраиваем параметры
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

                        return cap, source
                    time.sleep(0.1)

                cap.release()

        except Exception as e:
            print(f"Ошибка при открытии {source}: {e}")
            if cap:
                cap.release()

    raise RuntimeError("Не удалось открыть камеру после всех попыток")


def safe_camera_release(cap):
    """Безопасное освобождение камеры"""
    if cap is not None:
        try:
            # Сначала останавливаем захват
            cap.grab()
            time.sleep(0.1)

            # Затем освобождаем
            cap.release()
            time.sleep(0.1)

            print("Камера освобождена")
        except Exception as e:
            print(f"Ошибка при освобождении камеры: {e}")

    # Принудительная очистка
    force_release_camera()