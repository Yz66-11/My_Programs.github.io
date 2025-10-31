from ultralytics import YOLO

a1 = YOLO(r'/runs/detect/train3_Che_Li\weights\best.pt')

a1('课堂录像_1.mp4',save = True)