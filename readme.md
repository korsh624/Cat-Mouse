Алгоритм работы</br> 
Записываем видео softvare/yoloversion/writeVideo.py</br> 
если не роботом а камерой то меняем индекс камеры на 1</br> 
Через softvare/yoloversion/savecadr.py делаем фотки для датасета</br>  
предварительно очистить  softvare/yoloversion/out</br> 
Грузим фотки на roboflow, размечаем dataset и качаем в формате Yolo8</br> 
в папке softvare/yoloversion делаем: </br> 
git clone https://github.com/ultralytics/yolov5 (если такой папки нет).</br> 
cd yolov5</br> 
pip install -r requirements.txt  (если ранее не выполняли) </br> 
Сюда распаковываем архив с датасетом в папку softvare/yoloversion/yolov5/dataset</br> 
находясь в папке softvare/yoloversion/yolov5 запускаем обучение командой </br> 
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=100 imgsz=640 device=0  </br> 
device=0 говорит о том, что учить будем на видюхе.</br> 
Веса сохраняются в папку runs/detect/train/weights/best.pt



