import cv2
import numpy as np
import os
import threading
import queue
from ultralytics import YOLO
from deepface import DeepFace


class ProfessionalMonitor:
    def __init__(self, db_path="student_db.npy"):
        # 1. 模型加载
        self.face_detector = YOLO("yolov8n-face.pt")
        self.pose_model = YOLO("yolov8n-pose.pt")
        self.behavior_detector = YOLO("yolov8n.pt")

        # 2. 特征数据库加载
        if os.path.exists(db_path):
            self.known_db = np.load(db_path, allow_pickle=True).item()
            print(f"Database loaded: {len(self.known_db)} students.")
        else:
            self.known_db = {}
            print("Warning: student_db.npy not found.")

        # 3. 识别队列与字典 (直接用 track_id 映射，但增加刷新机制)
        self.task_queue = queue.Queue(maxsize=5)
        self.results_cache = {}  # {track_id: name}
        self.is_running = True

        threading.Thread(target=self._recognition_worker, daemon=True).start()

    def _recognition_worker(self):
        """核心识别工作线程"""
        while self.is_running:
            try:
                # 这里的 face_roi 必须是当前画面中实时截取的
                face_roi, track_id = self.task_queue.get(timeout=1)

                res = DeepFace.represent(
                    face_roi,
                    model_name="ArcFace",
                    enforce_detection=False,
                    detector_backend='opencv'
                )

                if res:
                    v_target = np.array(res[0]["embedding"], dtype=np.float32)
                    v_target /= np.linalg.norm(v_target)

                    best_name, max_sim = "Unknown", 0.45  # 识别门槛
                    for name, v_known in self.known_db.items():
                        sim = np.dot(v_target, v_known)
                        if sim > max_sim:
                            max_sim = sim
                            best_name = name

                    # 关键修改：直接强制更新该 ID 的显示结果
                    self.results_cache[track_id] = best_name
                else:
                    self.results_cache[track_id] = "Unknown"

                self.task_queue.task_done()
            except:
                continue

    def start(self, source=0):
        cap = cv2.VideoCapture(source)
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            h, w = frame.shape[:2]

            # 模型检测
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

                    # --- 强制刷新逻辑：大幅提高采样频率 ---
                    # 每 10 帧（约 0.3 秒）不管有没有结果，都送入后台识别
                    if frame_idx % 10 == 0:
                        margin = int((x2 - x1) * 0.2)
                        roi = frame[max(0, y1 - margin):min(h, y2 + margin), max(0, x1 - margin):min(w, x2 + margin)]
                        if roi.size > 0 and self.task_queue.qsize() < 3:
                            # 清除队列中可能存在的旧任务，确保只处理最新的脸
                            with self.task_queue.mutex:
                                self.task_queue.queue.clear()
                            self.task_queue.put((roi.copy(), tid))

                    # 获取名称，如果没有则默认 Unknown
                    name = self.results_cache.get(tid, "Scanning...")
                    status = "Normal"

                    # 基于 Pose 的睡觉检测
                    for person in pose_results[0]:
                        kpts = person.keypoints.data[0].cpu().numpy()
                        if kpts[5][2] > 0.5 and kpts[6][2] > 0.5:
                            avg_shoulder_y = (kpts[5][1] + kpts[6][1]) / 2
                            avg_eye_y = (kpts[1][1] + kpts[2][1]) / 2
                            p_box = person.boxes.xyxy[0].cpu().numpy()
                            if p_box[0] < cx < p_box[2]:
                                if avg_eye_y > avg_shoulder_y - 30:
                                    status = "Sleeping"

                    # 玩手机关联检测
                    for p in phones:
                        if abs((p[0] + p[2]) / 2 - cx) < 120 and abs((p[1] + p[3]) / 2 - cy) < 150:
                            status = "Using Phone"

                    # 颜色逻辑：识别成功且正常为绿，否则为红
                    if name != "Unknown" and name != "Scanning..." and status == "Normal":
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{name} | {status}", (x1, y1 - 10), 0, 0.6, color, 2)

            # --- 关键修改：如果画面中没检测到 ID，直接清空所有缓存 ---
            # 镜头挪开，旧名字不会留给下一个人
            if face_results[0].boxes.id is None:
                self.results_cache.clear()

            cv2.imshow("Monitor Final Version", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    monitor = ProfessionalMonitor()
    monitor.start()