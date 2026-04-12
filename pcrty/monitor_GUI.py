import cv2
import numpy as np
import os
import threading
import queue
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from datetime import datetime
from ultralytics import YOLO
from deepface import DeepFace

# 强制 FFmpeg 在 5 秒内如果无法打开流就返回，防止假死
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000000" # 单位为微秒
# =================================================+
# 1. 核心监测逻辑类 (增加身份继承优化)
# =================================================+
class ClassroomFinalSystem:
    def __init__(self, db_path="student_db.npy", gui_callback=None):
        self.face_detector = YOLO("yolov8n-face.pt")
        self.pose_model = YOLO("yolov8n-pose.pt")
        self.behavior_detector = YOLO("yolov8n.pt")
        self.gui_callback = gui_callback

        if os.path.exists(db_path):
            self.known_db = np.load(db_path, allow_pickle=True).item()
        else:
            self.known_db = {}

        self.task_queue = queue.Queue(maxsize=5)
        self.results_cache = {}

        # --- 新增：时空轨迹身份映射表 ---
        # 格式: {track_id: "姓名"}，只要追踪不断，身份就永久绑定
        self.identity_map = {}

        self.is_running = True
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

                    # 识别到有效身份后，立即更新映射表
                    self.results_cache[track_id] = best_name
                    if best_name != "Unknown":
                        self.identity_map[track_id] = best_name  # 绑定轨迹与身份
                        self.attendance.add(best_name)
                else:
                    self.results_cache[track_id] = "Unknown"
                self.task_queue.task_done()
            except:
                continue

    def process_frame(self, frame, frame_idx):
        h, w = frame.shape[:2]
        pose_results = self.pose_model.predict(frame, conf=0.5, verbose=False)
        behavior_results = self.behavior_detector.predict(frame, conf=0.4, verbose=False)
        face_results = self.face_detector.track(frame, persist=True, conf=0.5, verbose=False)
        phones = [p.xyxy[0].cpu().numpy() for p in behavior_results[0].boxes if int(p.cls[0]) == 67]

        # 清理已消失的 track_id（防止内存泄漏）
        active_ids = []

        if face_results[0].boxes.id is not None:
            boxes = face_results[0].boxes.xyxy.cpu().numpy()
            ids = face_results[0].boxes.id.cpu().numpy().astype(int)
            active_ids = ids.tolist()

            for box, tid in zip(boxes, ids):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                # 优先从 identity_map 获取已绑定身份
                # 即使现在脸被遮挡，只要之前的 tid 识别成功过，name 就不是 Unknown
                name = self.identity_map.get(tid, self.results_cache.get(tid, "Unknown"))

                # 只有当 identity_map 中还没这个人的时候，才触发识别任务
                if tid not in self.identity_map and frame_idx % 15 == 0:
                    margin = int((x2 - x1) * 0.2)
                    roi = frame[max(0, y1 - margin):min(h, y2 + margin), max(0, x1 - margin):min(w, x2 + margin)]
                    if roi.size > 0:
                        try:
                            self.task_queue.put((roi.copy(), tid), block=False)
                        except:
                            pass

                status = "Normal"
                # 行为判定：睡觉 (基于 Pose)
                for person in pose_results[0]:
                    kpts = person.keypoints.data[0].cpu().numpy()
                    if kpts[5][2] > 0.5 and kpts[6][2] > 0.5:
                        if (kpts[1][1] + kpts[2][1]) / 2 > (kpts[5][1] + kpts[6][1]) / 2 - 30:
                            p_box = person.boxes.xyxy[0].cpu().numpy()
                            if p_box[0] < cx < p_box[2]: status = "Sleeping"

                # 行为判定：手机
                for p in phones:
                    if abs((p[0] + p[2]) / 2 - cx) < 120 and abs((p[1] + p[3]) / 2 - cy) < 150:
                        status = "Using Phone"

                # 记录逻辑
                if status != "Normal":
                    if name not in self.record_locked:
                        self.record_locked[name] = {"Sleeping": False, "Using Phone": False}
                    if not self.record_locked[name].get(status, False):
                        self.violation_logs.append({
                            "name": name, "behavior": status, "time": datetime.now().strftime("%H:%M:%S")
                        })
                        self.record_locked[name][status] = True
                        if self.gui_callback: self.gui_callback(f"{name}: {status}")

                color = (0, 255, 0) if (name != "Unknown" and status == "Normal") else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{name}|{status}", (x1, y1 - 10), 0, 0.6, color, 2)

        # 清理不在画面中的 ID 缓存
        self.identity_map = {k: v for k, v in self.identity_map.items() if k in active_ids}
        return frame

    def _generate_report(self):
        report = {
            "summary": {"date": datetime.now().strftime("%Y-%m-%d"), "attendance": list(self.attendance)},
            "behavior_records": self.violation_logs
        }
        with open("classroom_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

# =================================================+
# 2. GUI 界面类 (增强容错版)
# =================================================+
class ClassroomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能课堂监控系统")
        self.root.geometry("1280x850")

        self.system = ClassroomFinalSystem(gui_callback=self.update_status_log)
        self.cap = None
        self.frame_idx = 0
        self.video_loop_running = False
        self.pending_source = None

        self.setup_ui()

    def setup_ui(self):
        self.video_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.video_frame.place(relx=0.01, rely=0.01, relwidth=0.72, relheight=0.78)
        self.video_label = tk.Label(self.video_frame, bg="black", text="等待信号接入...", fg="white")
        self.video_label.pack(expand=True, fill="both")

        self.status_frame = tk.LabelFrame(self.root, text="异常动态输出")
        self.status_frame.place(relx=0.74, rely=0.01, relwidth=0.25, relheight=0.78)
        self.status_log = tk.Text(self.status_frame, state='disabled', font=("Consolas", 10), bg="#f8f9fa")
        self.status_log.pack(expand=True, fill="both", padx=5, pady=5)

        self.control_panel = tk.LabelFrame(self.root, text="控制终端")
        self.control_panel.place(relx=0.01, rely=0.8, relwidth=0.98, relheight=0.18)

        tk.Label(self.control_panel, text="接入方式:").grid(row=0, column=0, padx=10, pady=10)
        self.source_type = tk.StringVar(value="camera")
        ttk.Radiobutton(self.control_panel, text="本地摄像头", variable=self.source_type, value="camera",
                        command=self.on_source_change).grid(row=0, column=1)
        ttk.Radiobutton(self.control_panel, text="本地文件", variable=self.source_type, value="file",
                        command=self.on_source_change).grid(row=0, column=2)
        ttk.Radiobutton(self.control_panel, text="网络视频流", variable=self.source_type, value="stream",
                        command=self.on_source_change).grid(row=0, column=3)

        self.url_entry = ttk.Entry(self.control_panel, width=60)
        self.url_entry.grid(row=1, column=1, columnspan=3, sticky="w", padx=5)
        self.url_entry.insert(0, "0")

        self.btn_browse = ttk.Button(self.control_panel, text="浏览文件", command=self.browse_file, state="disabled")
        self.btn_browse.grid(row=1, column=4, padx=5)

        self.btn_apply = ttk.Button(self.control_panel, text="✅ 应用/切换", command=self.apply_source)
        self.btn_apply.grid(row=1, column=5, padx=20)

        self.btn_report = ttk.Button(self.control_panel, text="📊 导出报告", command=self.show_report)
        self.btn_report.grid(row=1, column=6, padx=5)

    def on_source_change(self):
        stype = self.source_type.get()
        self.url_entry.delete(0, tk.END)
        if stype == "camera":
            self.url_entry.insert(0, "0")
            self.btn_browse.config(state="disabled")
        elif stype == "file":
            self.btn_browse.config(state="normal")
        else:
            self.url_entry.insert(0, "rtsp://")
            self.btn_browse.config(state="disabled")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mkv *.mov")])
        if filename:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, filename)

    def apply_source(self):
        raw_url = self.url_entry.get()
        if self.source_type.get() == "camera" and raw_url.isdigit():
            target = int(raw_url)
        else:
            target = raw_url

        # 启动预检查线程，防止 GUI 在尝试连接无效 RTSP 时假死
        self.btn_apply.config(state="disabled", text="正在尝试连接...")
        threading.Thread(target=self._check_source_worker, args=(target,), daemon=True).start()

    def _check_source_worker(self, target):
        """加入环境参数的连接检查"""
        # 如果是 RTSP 协议，增加 TCP 传输偏好（比 UDP 更稳定）
        if str(target).startswith("rtsp"):
            cap = cv2.VideoCapture(target, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)  # 设置 5 秒超时
        else:
            cap = cv2.VideoCapture(target)

        is_valid = cap.isOpened()
        if is_valid:
            ret, _ = cap.read()  # 尝试抓取一帧确认流是否真的有数据
            if not ret: is_valid = False

        cap.release()

        if is_valid:
            self.pending_source = target
            self.root.after(0, lambda: self.update_status_log(f"连接成功: {target}"))
            if not self.video_loop_running:
                self.video_loop_running = True
                self.root.after(0, self.update_frame)
        else:
            self.root.after(0, lambda: messagebox.showwarning("连接失败", "源无响应或地址错误，请检查网络"))
            self.root.after(0, lambda: self.btn_apply.config(state="normal", text="✅ 应用/切换"))

    def update_frame(self):
        if self.pending_source is not None:
            if self.cap: self.cap.release()
            self.cap = cv2.VideoCapture(self.pending_source)
            self.pending_source = None

        if self.video_loop_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_idx += 1
                    processed_frame = self.system.process_frame(frame, self.frame_idx)

                    cv2_img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2_img)

                    win_w = max(self.video_label.winfo_width(), 100)
                    win_h = max(self.video_label.winfo_height(), 100)
                    img = img.resize((win_w, win_h), Image.Resampling.LANCZOS)

                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.configure(image=imgtk)
                    self.video_label.image = imgtk
                    self.root.after(10, self.update_frame)
                else:
                    self.update_status_log("数据流中断或播放完毕")
                    self._stop_capture()
            except Exception as e:
                self.update_status_log(f"运行错误: {str(e)}")
                self._stop_capture()

    def _stop_capture(self):
        self.video_loop_running = False
        if self.cap: self.cap.release()
        self.video_label.config(image='', text="信号已断开")

    def update_status_log(self, message):
        self.status_log.config(state='normal')
        self.status_log.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.status_log.see('end')
        self.status_log.config(state='disabled')

    def show_report(self):
        self.system._generate_report()
        messagebox.showinfo("成功", "报告已保存")

    def on_closing(self):
        self.video_loop_running = False
        if self.cap: self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = ClassroomGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()