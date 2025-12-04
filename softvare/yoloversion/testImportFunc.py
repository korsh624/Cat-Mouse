import cv2
from eval import findSquare
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    ret,frame= findSquare(frame)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
