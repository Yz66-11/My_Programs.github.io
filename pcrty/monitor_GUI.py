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
import subprocess
import socket
import ipaddress
import time
import re
import hashlib
import concurrent.futures
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def align_face(frame, landmarks, min_size=112):
    if landmarks is None or len(landmarks) < 5:
        return None
    left_eye = landmarks[0][:2]
    right_eye = landmarks[1][:2]
    dY = right_eye[1] - left_eye[1]
    dX = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dY, dX))
    eye_dist = np.sqrt((dX ** 2) + (dY ** 2))
    desired_eye_dist = eye_dist * 1.5
    target_size = max(min_size, int(desired_eye_dist * 2.5))
    target_size = min(target_size, 256)
    desired_left_eye = (0.35, 0.35)
    desired_right_eye_x = 1.0 - desired_left_eye[0]
    desired_dist = desired_right_eye_x - desired_left_eye[0]
    desired_dist *= target_size
    scale = desired_dist / eye_dist if eye_dist > 0 else 1.0
    eyes_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
    M = cv2.getRotationMatrix2D(eyes_center, angle, scale)
    M[0, 2] += (target_size // 2) - eyes_center[0]
    M[1, 2] += (target_size // 2) - eyes_center[1]
    aligned = cv2.warpAffine(frame, M, (target_size, target_size), flags=cv2.INTER_CUBIC)
    return aligned

def detect_head_pose(landmarks):
    if landmarks is None or len(landmarks) < 5:
        return "normal", 0.0
    left_eye = landmarks[0][:2]
    right_eye = landmarks[1][:2]
    nose = landmarks[2][:2]
    left_mouth = landmarks[3][:2]
    right_mouth = landmarks[4][:2]
    eye_center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)
    mouth_center = ((left_mouth[0] + right_mouth[0]) / 2, (left_mouth[1] + right_mouth[1]) / 2)
    eye_width = np.linalg.norm(left_eye - right_eye)
    mouth_width = np.linalg.norm(left_mouth - right_mouth)
    nose_to_eyes = eye_center[1] - nose[1]
    nose_to_mouth = mouth_center[1] - nose[1]
    vertical_ratio = nose_to_eyes / (nose_to_mouth + 1e-6)
    eye_to_mouth_dist = mouth_center[1] - eye_center[1]
    face_height_estimate = eye_to_mouth_dist * 2.5
    face_width_estimate = eye_width * 2.5
    aspect_ratio = face_height_estimate / (face_width_estimate + 1e-6)
    pose_type = "normal"
    pose_score = 0.0
    if vertical_ratio < 0.3:
        pose_type = "looking_up"
        pose_score = abs(0.3 - vertical_ratio) / 0.3
    elif vertical_ratio > 1.5:
        pose_type = "looking_down"
        pose_score = min(1.0, (vertical_ratio - 1.5) / 1.0)
    if aspect_ratio < 0.8:
        pose_type = "looking_down"
        pose_score = max(pose_score, (0.8 - aspect_ratio) / 0.8)
    return pose_type, pose_score

class FaceEnhancer:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.frame_buffer = {}
        self.buffer_size = 3

    def enhance(self, face_roi, track_id=None, enhance_level="simple"):
        if face_roi is None or face_roi.size == 0:
            return face_roi
        enhanced = face_roi.copy()
        h, w = enhanced.shape[:2]
        
        min_size = 60 if enhance_level == "simple" else 80
        if h < min_size or w < min_size:
            scale = max(min_size / h, min_size / w)
            new_w, new_h = int(w * scale), int(h * scale)
            enhanced = cv2.resize(enhanced, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        if enhance_level == "full":
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, h=3, hColor=3, templateWindowSize=7, searchWindowSize=21)
            gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
            enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
            
            if track_id is not None:
                if track_id not in self.frame_buffer:
                    self.frame_buffer[track_id] = []
                self.frame_buffer[track_id].append(enhanced.copy())
                if len(self.frame_buffer[track_id]) > self.buffer_size:
                    self.frame_buffer[track_id].pop(0)
                if len(self.frame_buffer[track_id]) >= 3:
                    enhanced = self._multi_frame_fuse(self.frame_buffer[track_id])
        
        return enhanced

    def _multi_frame_fuse(self, frames):
        if len(frames) == 0:
            return None
        if len(frames) == 1:
            return frames[0]
        base = frames[-1].astype(np.float32)
        weights = np.exp(np.linspace(-1, 0, len(frames)))
        weights = weights / weights.sum()
        fused = np.zeros_like(base)
        for i, frame in enumerate(frames):
            fused += frame.astype(np.float32) * weights[i]
        fused = np.clip(fused, 0, 255).astype(np.uint8)
        return fused

    def clear_buffer(self, active_ids=None):
        if active_ids is None:
            self.frame_buffer.clear()
        else:
            self.frame_buffer = {k: v for k, v in self.frame_buffer.items() if k in active_ids}

# ---------- 本地 RTSP 服务器管理器（仅用于接收转推流，不推流本机摄像头） ----------
class MediaMTXManager:
    """管理 MediaMTX RTSP 服务器（仅用于接收转推）"""
    def __init__(self, mediamtx_path=None):
        if mediamtx_path is None:
            mediamtx_path = os.path.join(SCRIPT_DIR, "mediamtx.exe")
        self.mediamtx_path = mediamtx_path
        self.process = None

    def start(self):
        if self.is_running():
            return True
        if not os.path.exists(self.mediamtx_path):
            print(f"错误: 找不到 MediaMTX 程序 {self.mediamtx_path}")
            return False
        config_path = os.path.join(SCRIPT_DIR, "mediamtx.yml")
        if not os.path.exists(config_path):
            print(f"警告: 找不到配置文件 {config_path}，将使用空配置（API 可能不可用）")
        try:
            self.process = subprocess.Popen(
                [self.mediamtx_path, config_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            print("MediaMTX 服务器已启动。")
            return True
        except Exception as e:
            print(f"启动 MediaMTX 失败: {e}")
            return False

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
            print("MediaMTX 服务器已停止。")

    def is_running(self):
        return self.process is not None and self.process.poll() is None

# ---------- 外部流转推管理器 ----------
class RelayStreamManager:
    def __init__(self, mediamtx_mgr):
        self.mediamtx_mgr = mediamtx_mgr
        self.processes = {}  # {source_url: (local_rtsp_url, process)}

    def start_relay(self, source_url, local_rtsp_url=None):
        if source_url in self.processes:
            return self.processes[source_url][0]
        # 确保 RTSP 服务器已启动
        if not self.mediamtx_mgr.is_running():
            if not self.mediamtx_mgr.start():
                return None
        if not local_rtsp_url:
            hash_name = hashlib.md5(source_url.encode()).hexdigest()[:8]
            local_rtsp_url = f"rtsp://127.0.0.1:8554/relay_{hash_name}"
        ffmpeg_exe = os.path.join(SCRIPT_DIR, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_exe):
            ffmpeg_exe = "ffmpeg"
        cmd = [
            ffmpeg_exe, '-i', source_url,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',
            '-c:a', 'aac', '-b:a', '64k',
            '-f', 'rtsp', local_rtsp_url
        ]
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            self.processes[source_url] = (local_rtsp_url, proc)
            print(f"转推服务已启动: {source_url} -> {local_rtsp_url}")
            return local_rtsp_url
        except Exception as e:
            print(f"转推失败 {source_url}: {e}")
            return None

    def stop_all(self):
        for url, (_, proc) in self.processes.items():
            proc.terminate()
        self.processes.clear()

# ---------- 协议探测辅助函数 ----------
def get_camera_names():
    # 此函数不再用于本机推流，但保留以备其他用途（暂未使用）
    return []

def probe_rtsp_paths(ip, port, paths=['/test', '/stream', '/live', '/camera', '/h264', '/classroom', '/h264.sdp', '/video']):
    found = []
    ffprobe_exe = os.path.join(SCRIPT_DIR, "ffprobe.exe")
    if not os.path.exists(ffprobe_exe):
        ffprobe_exe = "ffprobe"
    for path in paths:
        if not path.startswith('/'):
            path = '/' + path
        url = f"rtsp://{ip}:{port}{path}"
        cmd = [ffprobe_exe, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type',
               '-of', 'default=nokey=1:noprint_wrappers=1', '-timeout', '2000000', url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'video' in result.stdout:
                found.append(url)
                print(f"发现 RTSP 流: {url}")
        except:
            pass
    return found

def probe_http_streams(ip, port):
    paths = ['/video', '/stream', '/mjpeg', '/live', '/h264', '/camera', '/h264.sdp']
    urls = []
    for path in paths:
        url = f"http://{ip}:{port}{path}"
        try:
            resp = requests.head(url, timeout=1)
            if resp.status_code == 200:
                content_type = resp.headers.get('Content-Type', '')
                if 'multipart/x-mixed-replace' in content_type or 'image/jpeg' in content_type:
                    urls.append(url)
                    print(f"发现 HTTP MJPEG 流: {url}")
        except:
            pass
    return urls

def probe_rtmp_streams(ip, port):
    paths = ['/live', '/stream', '/h264']
    urls = []
    ffprobe_exe = os.path.join(SCRIPT_DIR, "ffprobe.exe")
    if not os.path.exists(ffprobe_exe):
        ffprobe_exe = "ffprobe"
    for path in paths:
        url = f"rtmp://{ip}:{port}{path}"
        cmd = [ffprobe_exe, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type',
               '-of', 'default=nokey=1:noprint_wrappers=1', '-timeout', '2000000', url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'video' in result.stdout:
                urls.append(url)
                print(f"发现 RTMP 流: {url}")
        except:
            pass
    return urls

def scan_ports(ip, ports, timeout=0.1):
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                open_ports.append(port)
        except:
            pass
    return ip, open_ports

def scan_all_streams(target_network=None):
    """
    扫描局域网内所有视频源（RTSP/HTTP/RTMP），自动转推非RTSP源为本地RTSP。
    返回 (可用RTSP地址列表, RelayStreamManager实例)
    """
    # 创建 MediaMTX 管理器（用于接收转推）
    mediamtx_mgr = MediaMTXManager()
    relay_mgr = RelayStreamManager(mediamtx_mgr)
    found_urls = []

    # 确定扫描网段
    if target_network is None:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            ip_parts = local_ip.split('.')
            target_network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            print(f"自动检测到网络: {target_network}")
        except:
            print("无法自动检测网络，请手动输入网段")
            target_network = input("请输入网段: ").strip()
            if not target_network:
                return found_urls, relay_mgr

    try:
        network = ipaddress.ip_network(target_network, strict=False)
        ip_list = [str(ip) for ip in network.hosts()]
    except ValueError:
        print(f"无效网段: {target_network}")
        return found_urls, relay_mgr

    ports_to_scan = [554, 8554, 8080, 80, 8000, 8888, 1935]
    open_hosts = {}
    print(f"正在扫描 {target_network} 的 {len(ip_list)} 个 IP（多线程）...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_ports, ip, ports_to_scan, 0.1): ip for ip in ip_list}
        for future in concurrent.futures.as_completed(futures):
            ip, open_ports = future.result()
            if open_ports:
                open_hosts[ip] = open_ports
                for port in open_ports:
                    print(f"发现开放端口 {port} 的主机: {ip}")

    if not open_hosts:
        print("未发现开放相关端口的主机。")
        return found_urls, relay_mgr

    print("正在探测视频流路径...")
    def probe_target(ip, port):
        if port in [554, 8554]:
            rtsp_urls = probe_rtsp_paths(ip, port)
            for url in rtsp_urls:
                if url not in found_urls:
                    found_urls.append(url)
        elif port in [8080, 80, 8000, 8888]:
            http_urls = probe_http_streams(ip, port)
            for http_url in http_urls:
                cap = cv2.VideoCapture(http_url, cv2.CAP_FFMPEG)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        if http_url not in found_urls:
                            found_urls.append(http_url)
                            print(f"直接可用的 HTTP 流: {http_url}")
                    cap.release()
                else:
                    local_rtsp = relay_mgr.start_relay(http_url)
                    if local_rtsp and local_rtsp not in found_urls:
                        found_urls.append(local_rtsp)
        elif port == 1935:
            rtmp_urls = probe_rtmp_streams(ip, port)
            for rtmp_url in rtmp_urls:
                local_rtsp = relay_mgr.start_relay(rtmp_url)
                if local_rtsp and local_rtsp not in found_urls:
                    found_urls.append(local_rtsp)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for ip, ports in open_hosts.items():
            for port in ports:
                futures.append(executor.submit(probe_target, ip, port))
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return found_urls, relay_mgr

# ---------- 核心监测类（识别+扫描） ----------
class ClassroomFinalSystem:
    def __init__(self, db_path="student_db.npy", gui_callback=None):
        self.face_detector = YOLO("yolov8n-face.pt")
        self.pose_model = YOLO("yolov8n-pose.pt")
        self.behavior_detector = YOLO("yolov8n.pt")

        if os.path.exists(db_path):
            self.known_db = np.load(db_path, allow_pickle=True).item()
        else:
            self.known_db = {}

        self.task_queue = queue.Queue(maxsize=5)
        self.results_cache = {}
        self.identity_map = {}
        self.is_running = True
        self.face_enhancer = FaceEnhancer()
        self.source_type = "local"

        self.attendance = set()
        self.attendance_logs = []
        self.violation_logs = []
        self.violation_recorded = {}
        self.gui_callback = gui_callback

        self.attendance_confirm = {}
        self.attendance_confirm_threshold = 5
        self.attendance_fail_decrement = 1
        self.attendance_first_detect_time = {}
        self.behavior_confirm = {}
        self.behavior_confirm_threshold = 8
        self.behavior_decay_rate = 2
        self.behavior_time_window = 30
        self.behavior_first_detect_time = {}

        self.relay_manager = None

        threading.Thread(target=self._recognition_worker, daemon=True).start()

    def set_source_type(self, source_type):
        self.source_type = source_type

    def _recognition_worker(self):
        while self.is_running:
            try:
                task_data = self.task_queue.get(timeout=1)
                if len(task_data) == 4:
                    face_roi, track_id, landmarks, pose_type = task_data
                else:
                    face_roi, track_id = task_data
                    landmarks = None
                    pose_type = "normal"

                if landmarks is not None and len(landmarks) >= 5:
                    aligned_face = align_face(face_roi, landmarks)
                    if aligned_face is not None and aligned_face.size > 0:
                        face_roi = aligned_face

                enhance_level = "full" if self.source_type == "network" else "simple"
                face_roi = self.face_enhancer.enhance(face_roi, track_id, enhance_level)

                h, w = face_roi.shape[:2]
                if h < 40 or w < 40:
                    self.results_cache[track_id] = "Unknown"
                    self.task_queue.task_done()
                    continue

                res = DeepFace.represent(
                    face_roi, model_name="ArcFace",
                    enforce_detection=False, detector_backend='opencv'
                )
                if res:
                    v_target = np.array(res[0]["embedding"], dtype=np.float32)
                    v_target /= np.linalg.norm(v_target)

                    best_name = "Unknown"
                    max_sim = 0.40
                    for name, v_known in self.known_db.items():
                        sim = np.dot(v_target, v_known)
                        if sim > max_sim:
                            max_sim = sim
                            best_name = name

                    self.results_cache[track_id] = best_name
                    if best_name != "Unknown":
                        self.identity_map[track_id] = best_name
                        
                        if track_id not in self.attendance_confirm:
                            self.attendance_confirm[track_id] = {"name": best_name, "count": 0}
                            self.attendance_first_detect_time[track_id] = time.time()
                        
                        if self.attendance_confirm[track_id]["name"] == best_name:
                            self.attendance_confirm[track_id]["count"] += 1
                        else:
                            self.attendance_confirm[track_id] = {"name": best_name, "count": 1}
                            self.attendance_first_detect_time[track_id] = time.time()
                        
                        if self.attendance_confirm[track_id]["count"] >= self.attendance_confirm_threshold:
                            if best_name not in self.attendance:
                                self.attendance.add(best_name)
                                first_time = self.attendance_first_detect_time.get(track_id, time.time())
                                confirm_duration = time.time() - first_time
                                self.attendance_logs.append({
                                    "name": best_name,
                                    "check_in_time": datetime.now().strftime("%H:%M:%S"),
                                    "confirm_frames": self.attendance_confirm[track_id]["count"],
                                    "confirm_duration": f"{confirm_duration:.1f}s"
                                })
                    else:
                        if track_id in self.attendance_confirm:
                            self.attendance_confirm[track_id]["count"] -= self.attendance_fail_decrement
                            if self.attendance_confirm[track_id]["count"] <= 0:
                                del self.attendance_confirm[track_id]
                                if track_id in self.attendance_first_detect_time:
                                    del self.attendance_first_detect_time[track_id]
                else:
                    self.results_cache[track_id] = "Unknown"
                    if track_id in self.attendance_confirm:
                        self.attendance_confirm[track_id]["count"] -= self.attendance_fail_decrement
                        if self.attendance_confirm[track_id]["count"] <= 0:
                            del self.attendance_confirm[track_id]
                            if track_id in self.attendance_first_detect_time:
                                del self.attendance_first_detect_time[track_id]

                self.task_queue.task_done()
            except queue.Empty:
                continue
            except:
                continue

    def process_frame(self, frame, frame_idx):
        h, w = frame.shape[:2]

        pose_results = self.pose_model.predict(frame, conf=0.3, verbose=False)
        behavior_results = self.behavior_detector.predict(frame, conf=0.2, verbose=False)
        
        face_conf = 0.3 if self.source_type == "local" else 0.35
        face_results = self.face_detector.track(frame, persist=True, conf=face_conf, iou=0.6, verbose=False)

        phones = []
        if behavior_results[0].boxes is not None:
            phones = [p.xyxy[0].cpu().numpy() for p in behavior_results[0].boxes if int(p.cls[0]) == 67]

        active_ids = []
        if face_results[0].boxes.id is not None:
            boxes = face_results[0].boxes.xyxy.cpu().numpy()
            ids = face_results[0].boxes.id.cpu().numpy().astype(int)
            active_ids = ids.tolist()

            keypoints_data = None
            if hasattr(face_results[0], 'keypoints') and face_results[0].keypoints is not None:
                keypoints_data = face_results[0].keypoints.data

            for idx, (box, tid) in enumerate(zip(boxes, ids)):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                landmarks = None
                pose_type = "normal"
                if keypoints_data is not None and idx < len(keypoints_data):
                    kpts = keypoints_data[idx].cpu().numpy()
                    if kpts is not None and len(kpts) >= 5:
                        landmarks = kpts
                        pose_type, _ = detect_head_pose(landmarks)

                recognize_interval = 10 if self.source_type == "local" else 20
                should_recognize = False
                if tid not in self.identity_map:
                    if frame_idx % recognize_interval == 0:
                        should_recognize = True
                else:
                    name_in_map = self.identity_map.get(tid)
                    if name_in_map not in self.attendance:
                        if frame_idx % (recognize_interval + 5) == 0:
                            should_recognize = True
                
                if should_recognize:
                    margin = int((x2 - x1) * 0.2)
                    roi = frame[max(0, y1 - margin):min(h, y2 + margin),
                                max(0, x1 - margin):min(w, x2 + margin)]
                    if roi.size > 0:
                        with self.task_queue.mutex:
                            self.task_queue.queue.clear()
                        try:
                            self.task_queue.put((roi.copy(), tid, landmarks, pose_type), block=False)
                        except:
                            pass

                name = self.identity_map.get(tid, self.results_cache.get(tid, "Unknown"))
                status = "Normal"

                for person in pose_results[0]:
                    if person.keypoints is None:
                        continue
                    kpts = person.keypoints.data[0].cpu().numpy()
                    if kpts[5][2] > 0.5 and kpts[6][2] > 0.5:
                        avg_shoulder_y = (kpts[5][1] + kpts[6][1]) / 2
                        avg_eye_y = (kpts[1][1] + kpts[2][1]) / 2
                        p_box = person.boxes.xyxy[0].cpu().numpy()
                        if p_box[0] < cx < p_box[2] and avg_eye_y > avg_shoulder_y - 30:
                            status = "Sleeping"
                            break

                for p in phones:
                    if abs((p[0] + p[2]) / 2 - cx) < 120 and abs((p[1] + p[3]) / 2 - cy) < 150:
                        status = "Using Phone"
                        break

                if status != "Normal" and name != "Unknown":
                    behavior_key = f"{tid}_{status}"
                    
                    if behavior_key not in self.behavior_confirm:
                        self.behavior_confirm[behavior_key] = 0
                        self.behavior_first_detect_time[behavior_key] = time.time()
                    
                    self.behavior_confirm[behavior_key] += 1
                    
                    for key in list(self.behavior_confirm.keys()):
                        parts = key.split("_", 1)
                        if len(parts) == 2:
                            other_tid, other_status = parts
                            if other_tid == str(tid) and other_status != status:
                                self.behavior_confirm[key] -= self.behavior_decay_rate
                                if self.behavior_confirm[key] <= 0:
                                    del self.behavior_confirm[key]
                                    if key in self.behavior_first_detect_time:
                                        del self.behavior_first_detect_time[key]
                    
                    if self.behavior_confirm[behavior_key] >= self.behavior_confirm_threshold:
                        first_time = self.behavior_first_detect_time.get(behavior_key, time.time())
                        time_elapsed = time.time() - first_time
                        
                        if time_elapsed <= self.behavior_time_window:
                            record_key = f"{name}_{status}"
                            if record_key not in self.violation_recorded:
                                self.violation_logs.append({
                                    "name": name,
                                    "behavior": status,
                                    "first_detected": datetime.now().strftime("%H:%M:%S"),
                                    "confirm_duration": f"{time_elapsed:.1f}s"
                                })
                                self.violation_recorded[record_key] = True
                                if self.gui_callback:
                                    self.gui_callback(f"{name} - {status}")
                        else:
                            self.behavior_confirm[behavior_key] = self.behavior_confirm_threshold // 2
                            self.behavior_first_detect_time[behavior_key] = time.time()
                else:
                    if tid in self.behavior_confirm or any(k.startswith(f"{tid}_") for k in self.behavior_confirm):
                        keys_to_decay = [k for k in self.behavior_confirm if k.startswith(f"{tid}_")]
                        for k in keys_to_decay:
                            self.behavior_confirm[k] -= self.behavior_decay_rate
                            if self.behavior_confirm[k] <= 0:
                                del self.behavior_confirm[k]
                                if k in self.behavior_first_detect_time:
                                    del self.behavior_first_detect_time[k]

                color = (0, 255, 0) if (name != "Unknown" and status == "Normal") else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{name}|{status}", (x1, y1 - 10), 0, 0.6, color, 2)

        if not active_ids:
            self.results_cache.clear()
            self.identity_map.clear()
            self.face_enhancer.clear_buffer()
            self.attendance_confirm.clear()
            self.attendance_first_detect_time.clear()
            self.behavior_confirm.clear()
            self.behavior_first_detect_time.clear()
        else:
            self.results_cache = {k: v for k, v in self.results_cache.items() if k in active_ids}
            self.identity_map = {k: v for k, v in self.identity_map.items() if k in active_ids}
            self.face_enhancer.clear_buffer(active_ids)
            self.attendance_confirm = {k: v for k, v in self.attendance_confirm.items() if k in active_ids}
            self.attendance_first_detect_time = {k: v for k, v in self.attendance_first_detect_time.items() if k in active_ids}
            self.behavior_confirm = {k: v for k, v in self.behavior_confirm.items() if int(k.split("_")[0]) in active_ids}
            self.behavior_first_detect_time = {k: v for k, v in self.behavior_first_detect_time.items() if int(k.split("_")[0]) in active_ids}

        return frame

    def _generate_report(self):
        report = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attendance_records": {
                "total_count": len(self.attendance),
                "students": self.attendance_logs
            },
            "behavior_records": {
                "total_count": len(self.violation_logs),
                "violations": self.violation_logs
            }
        }
        with open("classroom_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

    def scan_and_connect(self, gui_callback):
        """扫描并弹出选择框，返回用户选择的流地址或 None"""
        gui_callback("开始智能扫描，请稍候...")
        found_urls, relay_mgr = scan_all_streams()
        self.relay_manager = relay_mgr
        if not found_urls:
            gui_callback("未发现任何可用视频流")
            return None
        # 弹出选择窗口
        choice_win = tk.Toplevel()
        choice_win.title("选择视频源")
        choice_win.geometry("600x400")
        tk.Label(choice_win, text="发现以下可用流，请选择:").pack(pady=10)
        listbox = tk.Listbox(choice_win, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for url in found_urls:
            listbox.insert(tk.END, url)
        result = [None]
        def on_ok():
            sel = listbox.curselection()
            if sel:
                result[0] = found_urls[sel[0]]
            choice_win.destroy()
        def on_cancel():
            choice_win.destroy()
        tk.Button(choice_win, text="连接", command=on_ok).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(choice_win, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=20, pady=10)
        choice_win.wait_window()
        return result[0]

    def reset_tracker(self):
        self.face_detector = YOLO("yolov8n-face.pt")
        self.results_cache.clear()
        self.identity_map.clear()
        self.face_enhancer.clear_buffer()

    def cleanup(self):
        self.is_running = False
        if self.relay_manager:
            self.relay_manager.stop_all()
        # 停止 MediaMTX（如果有运行）
        # 由于 MediaMTX 在 scan_all_streams 中创建，我们无法直接访问，但可以通过全局单例？简化：不主动停止，因为程序退出时会自动终止子进程
        # 但为了干净退出，可以尝试查找并终止 mediamtx 进程（可选）

# ---------- GUI 界面 ----------
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

        # 第一行：接入方式选择
        tk.Label(self.control_panel, text="接入方式:").grid(row=0, column=0, padx=10, pady=5)
        self.source_type = tk.StringVar(value="camera")
        ttk.Radiobutton(self.control_panel, text="本地摄像头", variable=self.source_type, value="camera",
                        command=self.on_source_change).grid(row=0, column=1)
        ttk.Radiobutton(self.control_panel, text="本地文件", variable=self.source_type, value="file",
                        command=self.on_source_change).grid(row=0, column=2)
        ttk.Radiobutton(self.control_panel, text="网络视频流", variable=self.source_type, value="stream",
                        command=self.on_source_change).grid(row=0, column=3)

        # 第二行：输入框和按钮
        self.url_entry = ttk.Entry(self.control_panel, width=60)
        self.url_entry.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        self.url_entry.insert(0, "0")

        self.btn_browse = ttk.Button(self.control_panel, text="浏览文件", command=self.browse_file, state="disabled")
        self.btn_browse.grid(row=1, column=4, padx=5)

        self.btn_apply = ttk.Button(self.control_panel, text="应用/切换", command=self.apply_source)
        self.btn_apply.grid(row=1, column=5, padx=20)

        self.btn_scan = ttk.Button(self.control_panel, text="智能扫描", command=self.scan_devices)
        self.btn_scan.grid(row=1, column=6, padx=5)

        self.btn_report = ttk.Button(self.control_panel, text="导出报告", command=self.show_report)
        self.btn_report.grid(row=1, column=7, padx=5)

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

        self.btn_apply.config(state="disabled", text="正在连接...")
        if self.video_loop_running:
            self._stop_capture()
        threading.Thread(target=self._check_source_worker, args=(target,), daemon=True).start()

    def _check_source_worker(self, target):
        target_str = str(target)
        if target_str.startswith("rtsp") or target_str.startswith("rtmp") or target_str.startswith("http"):
            cap = cv2.VideoCapture(target, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            self.system.set_source_type("network")
        elif target_str.isdigit():
            cap = cv2.VideoCapture(int(target))
            self.system.set_source_type("local")
        else:
            cap = cv2.VideoCapture(target)
            self.system.set_source_type("network")

        is_valid = cap.isOpened()
        if is_valid:
            ret, _ = cap.read()
            if not ret:
                is_valid = False
        cap.release()

        if is_valid:
            self.pending_source = target
            self.root.after(0, lambda: self.update_status_log(f"连接成功: {target}"))
            self.root.after(0, lambda: self.btn_apply.config(state="normal", text="应用/切换"))
            if not self.video_loop_running:
                self.video_loop_running = True
                self.root.after(0, self.update_frame)
        else:
            self.root.after(0, lambda: messagebox.showwarning("连接失败", "源无响应或地址错误，请检查网络"))
            self.root.after(0, lambda: self.btn_apply.config(state="normal", text="应用/切换"))

    def scan_devices(self):
        def scan_task():
            selected_url = self.system.scan_and_connect(self.update_status_log)
            if selected_url:
                self.update_status_log(f"选择连接: {selected_url}")
                self.system.set_source_type("network")
                if self.video_loop_running:
                    self._stop_capture()
                self.pending_source = selected_url
                self.video_loop_running = True
                self.root.after(0, self.update_frame)
            else:
                self.update_status_log("扫描未选择任何流")
        threading.Thread(target=scan_task, daemon=True).start()

    def update_frame(self):
        if self.pending_source is not None:
            if self.cap:
                self.cap.release()
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
        if self.cap:
            self.cap.release()
        self.system.reset_tracker()
        self.video_label.config(image='', text="信号已断开")
        self.btn_apply.config(state="normal", text="应用/切换")

    def update_status_log(self, message):
        self.status_log.config(state='normal')
        self.status_log.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.status_log.see('end')
        self.status_log.config(state='disabled')

    def show_report(self):
        self.system._generate_report()
        messagebox.showinfo("成功", "报告已保存为 classroom_report.json")

    def on_closing(self):
        self.video_loop_running = False
        if self.cap:
            self.cap.release()
        self.system.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    app = ClassroomGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()