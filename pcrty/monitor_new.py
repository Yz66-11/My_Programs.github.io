import cv2
import numpy as np
import os
import threading
import queue
import json
from datetime import datetime
from ultralytics import YOLO
from deepface import DeepFace


class ClassroomFinalSystem:
    def __init__(self, db_path="student_db.npy"):
        # 1. 模型加載
        self.face_detector = YOLO("yolov8n-face.pt")
        self.pose_model = YOLO("yolov8n-pose.pt")
        self.behavior_detector = YOLO("yolov8n.pt")

        # 2. 特徵數據庫
        if os.path.exists(db_path):
            self.known_db = np.load(db_path, allow_pickle=True).item()
        else:
            self.known_db = {}

        # 3. 識別隊列
        self.task_queue = queue.Queue(maxsize=5)
        self.results_cache = {}  # {track_id: name}
        self.is_running = True

        # 4. 報告數據結構與行為去重字典
        self.attendance = set()
        self.violation_logs = []
        self.record_locked = {}

        threading.Thread(target=self._recognition_worker, daemon=True).start()

    def _recognition_worker(self):
        while self.is_running:
            try:
                face_roi, track_id = self.task_queue.get(timeout=1)
                res = DeepFace.represent(face_roi, model_name="ArcFace",
                                         enforce_detection=False, detector_backend='opencv')
                if res:
                    v_target = np.array(res[0]["embedding"], dtype=np.float32)
                    v_target /= np.linalg.norm(v_target)
                    best_name, max_sim = "Unknown", 0.45
                    for name, v_known in self.known_db.items():
                        sim = np.dot(v_target, v_known)
                        if sim > max_sim:
                            max_sim = sim
                            best_name = name
                    self.results_cache[track_id] = best_name
                    if best_name != "Unknown":
                        self.attendance.add(best_name)
                else:
                    self.results_cache[track_id] = "Unknown"
                self.task_queue.task_done()
            except:
                continue

    def start(self, source=0):
        # 核心修改：source 可以是 0 (攝像頭) 或 "video.mp4" (路徑)
        cap = cv2.VideoCapture(source)

        # 針對視頻文件優化：如果 source 是字符串，獲取視頻原有的 FPS
        is_video_file = isinstance(source, str)

        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("視頻結束或無法讀取源")
                break

            frame_idx += 1
            h, w = frame.shape[:2]

            pose_results = self.pose_model.predict(frame, conf=0.5, verbose=False)
            behavior_results = self.behavior_detector.predict(frame, conf=0.4, verbose=False)
            face_results = self.face_detector.track(frame, persist=True, conf=0.5, verbose=False)
            phones = [p.xyxy[0].cpu().numpy() for p in behavior_results[0].boxes if int(p.cls[0]) == 67]

            if face_results[0].boxes.id is not None:
                boxes = face_results[0].boxes.xyxy.cpu().numpy()
                ids = face_results[0].boxes.id.cpu().numpy().astype(int)

                for box, tid in zip(boxes, ids):
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                    if frame_idx % 10 == 0:
                        margin = int((x2 - x1) * 0.2)
                        roi = frame[max(0, y1 - margin):min(h, y2 + margin), max(0, x1 - margin):min(w, x2 + margin)]
                        if roi.size > 0:
                            with self.task_queue.mutex:
                                self.task_queue.queue.clear()
                            try:
                                self.task_queue.put((roi.copy(), tid), block=False)
                            except:
                                pass

                    raw_name = self.results_cache.get(tid, "Unknown")
                    name = "Unknown" if raw_name == "Scanning..." else raw_name
                    status = "Normal"

                    for person in pose_results[0]:
                        kpts = person.keypoints.data[0].cpu().numpy()
                        if kpts[5][2] > 0.5 and kpts[6][2] > 0.5:
                            avg_shoulder_y = (kpts[5][1] + kpts[6][1]) / 2
                            avg_eye_y = (kpts[1][1] + kpts[2][1]) / 2
                            p_box = person.boxes.xyxy[0].cpu().numpy()
                            if p_box[0] < cx < p_box[2] and avg_eye_y > avg_shoulder_y - 30:
                                status = "Sleeping"

                    for p in phones:
                        if abs((p[0] + p[2]) / 2 - cx) < 120 and abs((p[1] + p[3]) / 2 - cy) < 150:
                            status = "Using Phone"

                    if status != "Normal":
                        if name not in self.record_locked:
                            self.record_locked[name] = {"Sleeping": False, "Using Phone": False}

                        if not self.record_locked[name].get(status, False):
                            self.violation_logs.append({
                                "name": name,
                                "behavior": status,
                                "first_detected": datetime.now().strftime("%H:%M:%S")
                            })
                            self.record_locked[name][status] = True

                    color = (0, 255, 0) if (name != "Unknown" and status == "Normal") else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{name}|{status}", (x1, y1 - 10), 0, 0.6, color, 2)

            if face_results[0].boxes.id is None:
                self.results_cache.clear()

            cv2.imshow("Smart Classroom Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self._generate_report()
        cap.release()
        cv2.destroyAllWindows()

    def _generate_report(self):
        report = {
            "summary": {"date": datetime.now().strftime("%Y-%m-%d"), "attendance": list(self.attendance)},
            "behavior_records": self.violation_logs
        }
        with open("classroom_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        print("Report saved to classroom_report.json")


if __name__ == "__main__":
    system = ClassroomFinalSystem()

    # 用戶自主選擇邏輯
    print("=== 課堂監控系統 ===")
    print("1. 實時攝像頭監控")
    print("2. 載入視頻文件監控")
    choice = input("請選擇 (1/2): ")

    if choice == "1":
        system.start(source=0)  # 默認攝像頭 ID
    elif choice == "2":
        video_path = input("請輸入視頻文件路徑 (例如: test.mp4): ")
        if os.path.exists(video_path):
            system.start(source=video_path)  # 傳入視頻路徑
        else:
            print("文件路徑不存在")
    else:
        print("無效選擇")