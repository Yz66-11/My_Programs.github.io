import cv2

from ultralytics import YOLO

model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print('摄像头读取失败')
        break

    results = model(frame,stream = True)

    for r in results:
        annotated_frame = r.plot()

        cv2.imshow('YOLO RFeal-Time Detection', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()