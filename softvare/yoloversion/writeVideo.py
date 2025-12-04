import cv2
import numpy as np

# 1. Создаем объект VideoCapture для доступа к камере
# Индекс 0 обычно означает встроенную веб-камеру. Используйте 1, 2 и т.д. для других камер.
cap = cv2.VideoCapture(0)

# Проверяем, удалось ли открыть камеру
if not cap.isOpened():
    print("Ошибка: Не удалось получить доступ к камере.")
    exit()

# 2. Получаем свойства кадра (ширину, высоту и FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 20.0 # Устанавливаем FPS по умолчанию, если не удалось определить.

# 3. Определяем кодек и создаем объект VideoWriter для записи видео
# Кодек 'mp4v' подходит для формата .mp4. Для .avi можно использовать 'XVID'.
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

print(f"Начало записи видео в файл output.mp4 с разрешением {frame_width}x{frame_height} и FPS {fps}")

# 4. Захватываем кадры в цикле
while True:
    # Читаем кадр с камеры
    ret, frame = cap.read()

    if not ret:
        print("Не удалось получить кадр (поток завершен?). Выход...")
        break

    # Записываем кадр в выходной файл
    out.write(frame)

    # Отображаем кадр в окне (необязательно)
    cv2.imshow('Camera Feed - Recording (Press "q" to stop)', frame)

    # Останавливаем запись при нажатии клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 5. Освобождаем ресурсы
cap.release()
out.release()
cv2.destroyAllWindows()

print("Запись видео завершена.")