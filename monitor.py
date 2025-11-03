#monitor.py
import cv2
import numpy as np
import os
import time
from datetime import datetime
from collections import defaultdict
from ultralytics import YOLO
import json


class FaceRecognizer:
    """
    人脸识别器
    功能: 使用YOLO检测人脸，并通过简单的特征匹配进行识别
    特点:
    - 使用YOLO进行人脸检测
    - 基于人脸位置和外观特征进行识别
    - 适合教室环境下的人脸识别
    """

    def __init__(self, model_path):
        """
        初始化识别器
        model_path: YOLO模型路径 (训练好的人脸检测模型)
        """
        self.model = YOLO(model_path)
        self.known_faces = {}  # 存储已知人脸信息
        self.recognition_threshold = 0.7  # 识别阈值

    def register_students(self, student_photos_dir):
        """
        注册学生照片
        功能: 从学生照片目录加载并提取人脸特征
        参数: student_photos_dir - 学生照片目录路径
        要求: 每张照片文件名格式: 学生ID.jpg
        """
        print(f"开始注册学生照片从: {student_photos_dir}")

        if not os.path.exists(student_photos_dir):
            print(f"错误: 目录不存在 {student_photos_dir}")
            return False

        registered_count = 0
        for filename in os.listdir(student_photos_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                student_id = os.path.splitext(filename)[0]
                image_path = os.path.join(student_photos_dir, filename)

                # 提取人脸特征
                features = self._extract_face_features(image_path)
                if features is not None:
                    self.known_faces[student_id] = features
                    registered_count += 1
                    print(f"注册学生: {student_id}")
                else:
                    print(f"警告: 无法从 {filename} 提取人脸特征")

        print(f"成功注册 {registered_count} 个学生")
        return registered_count > 0

    def _extract_face_features(self, image_path):
        """
        提取人脸特征
        方法: 使用YOLO检测人脸，然后提取简化特征
        特征包括: 人脸位置、大小、颜色直方图等
        """
        try:
            # 使用YOLO检测人脸
            results = self.model(image_path, verbose=False)

            if len(results) == 0 or results[0].boxes is None:
                return None

            # 获取第一个人脸检测框
            boxes = results[0].boxes
            if len(boxes) == 0:
                return None

            # 选择置信度最高的人脸
            best_idx = np.argmax([box.conf.item() for box in boxes])
            bbox = boxes.xyxy[best_idx].cpu().numpy()

            # 读取图片计算特征
            img = cv2.imread(image_path)
            if img is None:
                return None

            x1, y1, x2, y2 = map(int, bbox)
            face_region = img[y1:y2, x1:x2]

            if face_region.size == 0:
                return None

            # 计算简化特征
            features = self._compute_simple_features(face_region, bbox, img.shape)
            return features

        except Exception as e:
            print(f"提取特征错误 {image_path}: {e}")
            return None

    def _compute_simple_features(self, face_region, bbox, img_shape):
        """
        计算简化特征
        特征组成:
        - 人脸位置 (相对于图片大小)
        - 人脸宽高比例
        - 颜色直方图
        - 灰度特征
        """
        img_h, img_w = img_shape[:2]
        x1, y1, x2, y2 = bbox

        # 1. 位置特征 (归一化)
        center_x = (x1 + x2) / 2 / img_w
        center_y = (y1 + y2) / 2 / img_h
        width = (x2 - x1) / img_w
        height = (y2 - y1) / img_h

        # 2. 宽高比
        aspect_ratio = width / height if height > 0 else 0

        # 3. 颜色直方图特征 (简化)
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_face], [0], None, [16], [0, 256])
        hist = hist.flatten() / (hist.sum() + 1e-8)  # 归一化

        # 4. 组合所有特征
        position_features = [center_x, center_y, width, height, aspect_ratio]
        all_features = np.concatenate([position_features, hist])

        return all_features

    def recognize_faces(self, frame):
        """
        在视频帧中识别人脸
        返回: 识别结果列表, 每个元素包含学生ID和置信度
        """
        results = []

        try:
            # YOLO人脸检测
            detections = self.model(frame, verbose=False)

            if len(detections) == 0 or detections[0].boxes is None:
                return results

            boxes = detections[0].boxes
            for i, box in enumerate(boxes):
                confidence = box.conf.item()
                bbox = box.xyxy[0].cpu().numpy()

                # 提取当前人脸特征
                x1, y1, x2, y2 = map(int, bbox)
                face_region = frame[y1:y2, x1:x2]

                if face_region.size == 0:
                    continue

                current_features = self._compute_simple_features(face_region, bbox, frame.shape)
                if current_features is None:
                    continue

                # 与已知人脸匹配
                match_result = self._match_face(current_features)

                results.append({
                    'student_id': match_result['student_id'],
                    'confidence': match_result['confidence'],
                    'bbox': bbox,
                    'detection_confidence': confidence,
                    'timestamp': datetime.now()
                })

        except Exception as e:
            print(f"人脸识别错误: {e}")

        return results

    def _match_face(self, current_features):
        """
        人脸匹配 - 使用欧氏距离
        返回匹配的学生ID和置信度
        """
        best_match = 'unknown'
        best_distance = float('inf')

        for student_id, stored_features in self.known_faces.items():
            # 计算欧氏距离
            distance = np.linalg.norm(current_features - stored_features)

            if distance < best_distance:
                best_distance = distance
                best_match = student_id

        # 转换为置信度 (距离越小，置信度越高)
        confidence = max(0, 1 - best_distance / 10)  # 调整除数来调节置信度范围

        if confidence < self.recognition_threshold:
            best_match = 'unknown'
            confidence = 0

        return {'student_id': best_match, 'confidence': confidence}


class SimpleClassroomMonitor:
    """
    功能:
    - 人脸识别考勤
    - 手机使用检测
    - 生成简单报告
    """

    def __init__(self, face_model_path, behavior_model_path, student_photos_dir, output_dir = "rec_res"):
        """
        初始化监测系统
        face_model_path: 人脸检测模型路径
        behavior_model_path: 行为检测模型路径
        student_photos_dir: 学生照片目录
        """
        # 初始化识别器
        self.face_recognizer = FaceRecognizer(face_model_path)
        self.behavior_detector = YOLO(behavior_model_path)

        # 注册学生
        self.face_recognizer.register_students(student_photos_dir)

        # 记录系统
        self.attendance = defaultdict(list)  # 考勤记录
        self.phone_usage = defaultdict(list)  # 手机使用记录
        self.detection_log = []  # 检测日志

        # 手机类别ID (需要在训练时确定)
        self.phone_class_id = 67  # 常见YOLO手机类别ID，根据实际调整

        self.output_dir = output_dir

        print("课堂监测系统初始化完成")

    def process_video(self, video_source, duration=300, output_dir=None):
        """
        处理视频流
        video_source: 视频文件路径或摄像头ID
        duration: 处理时长(秒)
        output_dir: 输出目录(可选)
        """
        print(f"开始处理视频: {video_source}")

        # 打开视频
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"错误: 无法打开视频源 {video_source}")
            return

        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break

            # 处理当前帧
            self._process_frame(frame, frame_count)

            frame_count += 1

            # 每30帧显示进度
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                print(f"处理进度: {frame_count}帧, 耗时: {elapsed:.1f}秒")

        cap.release()
        print(f"视频处理完成: 共处理 {frame_count} 帧")

        # 保存结果
        if output_dir:
            self.save_results(output_dir)

    def _process_frame(self, frame, frame_count):
        """
        处理单帧图像
        """
        current_time = datetime.now()

        # 1. 人脸识别
        face_results = self.face_recognizer.recognize_faces(frame)

        # 记录考勤
        for face in face_results:
            if face['student_id'] != 'unknown':
                self.attendance[face['student_id']].append({
                    'time': current_time,
                    'frame': frame_count,
                    'confidence': face['confidence']
                })

        # 2. 行为检测
        behavior_results = self.behavior_detector(frame, verbose=False)

        # 检测手机使用
        if (len(behavior_results) > 0 and
                behavior_results[0].boxes is not None):

            for box in behavior_results[0].boxes:
                class_id = int(box.cls[0])
                if class_id == self.phone_class_id:
                    self._detect_phone_usage(box, face_results, frame_count)

        # 3. 记录检测日志
        self.detection_log.append({
            'frame': frame_count,
            'time': current_time,
            'faces_detected': len(face_results),
            'known_faces': len([f for f in face_results if f['student_id'] != 'unknown'])
        })

    def _detect_phone_usage(self, phone_box, face_results, frame_count):
        """
        检测手机使用行为
        方法: 找到距离手机最近的学生，关联手机使用行为
        """
        phone_bbox = phone_box.xyxy[0].cpu().numpy()
        phone_confidence = phone_box.conf.item()

        # 计算手机中心点
        phone_center = np.array([
            (phone_bbox[0] + phone_bbox[2]) / 2,
            (phone_bbox[1] + phone_bbox[3]) / 2
        ])

        # 找到最近的学生
        nearest_student = None
        min_distance = float('inf')

        for face in face_results:
            if face['student_id'] != 'unknown':
                face_bbox = face['bbox']
                face_center = np.array([
                    (face_bbox[0] + face_bbox[2]) / 2,
                    (face_bbox[1] + face_bbox[3]) / 2
                ])

                distance = np.linalg.norm(phone_center - face_center)
                if distance < min_distance:
                    min_distance = distance
                    nearest_student = face['student_id']

        # 如果距离足够近，记录手机使用
        if nearest_student and min_distance < 250:  # 距离阈值，可调整
            self.phone_usage[nearest_student].append({
                'time': datetime.now(),
                'frame': frame_count,
                'phone_confidence': phone_confidence,
                'distance': min_distance
            })

    def generate_report(self):
        """
        生成监测报告
        返回: 包含考勤和行为统计的字典
        """
        total_students = len(self.face_recognizer.known_faces)
        detected_students = len(self.attendance)

        # 计算考勤率
        attendance_rate = detected_students / total_students if total_students > 0 else 0

        # 统计手机使用
        phone_users = len(self.phone_usage)
        total_phone_events = sum(len(events) for events in self.phone_usage.values())

        report = {
            'summary': {
                'total_students': total_students,
                'present_students': detected_students,
                'attendance_rate': round(attendance_rate, 3),
                'phone_users_count': phone_users,
                'total_phone_events': total_phone_events,
                'analysis_duration_frames': len(self.detection_log),
                'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'attendance_details': {},
            'behavior_details': {}
        }

        # 详细考勤信息
        for student_id in self.face_recognizer.known_faces.keys():
            records = self.attendance.get(student_id, [])
            phone_records = self.phone_usage.get(student_id, [])

            report['attendance_details'][student_id] = {
                'detected': len(records) > 0,
                'detection_count': len(records),
                'first_detection': records[0]['time'].strftime('%H:%M:%S') if records else 'None',
                'last_detection': records[-1]['time'].strftime('%H:%M:%S') if records else 'None'
            }

            report['behavior_details'][student_id] = {
                'phone_usage_count': len(phone_records),
                'phone_usage_times': [r['time'].strftime('%H:%M:%S') for r in phone_records[:5]]  # 只显示前5次
            }

        return report

    def save_results(self, output_dir):
        """
        保存结果到文件
        """
        os.makedirs(output_dir, exist_ok=True)

        # 生成报告
        report = self.generate_report()

        # 保存JSON报告
        report_path = os.path.join(output_dir, 'classroom_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        # 保存简化的文本报告
        text_report_path = os.path.join(output_dir, 'summary.txt')
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write("课堂监测报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"总学生数: {report['summary']['total_students']}\n")
            f.write(f"出勤学生: {report['summary']['present_students']}\n")
            f.write(f"出勤率: {report['summary']['attendance_rate']:.1%}\n")
            f.write(f"使用手机学生: {report['summary']['phone_users_count']}\n")
            f.write(f"手机使用次数: {report['summary']['total_phone_events']}\n")
            f.write(f"分析时长: {report['summary']['analysis_duration_frames']} 帧\n")

        print(f"结果已保存到: {output_dir}")


# 使用示例
def main():
    """
    使用说明:
    1. 准备两个YOLO模型:
       - 人脸检测模型 (训练好的)
       - 行为检测模型 (可用的YOLO预训练模型)

    2. 准备学生照片目录

    3. 运行监测系统
    """

    # 配置路径 - 请根据实际情况修改
    face_model = "runs/train/class_monitor/weights/best.pt"  # 训练好的人脸检测模型
    behavior_model = "yolov8n.pt"  # 行为检测模型
    student_photos = "student_photos"  # 学生照片目录
    video_source = "课堂录像_1.mp4"  # 视频文件或摄像头ID

    # 创建监测系统
    monitor = SimpleClassroomMonitor(
        face_model_path=face_model,
        behavior_model_path=behavior_model,
        student_photos_dir=student_photos
    )

    # 处理视频
    monitor.process_video(
        video_source=video_source,
        duration=300,  # 处理5分钟
        output_dir="results"  # 输出目录
    )

    # 打印简要报告
    report = monitor.generate_report()
    print("\n" + "=" * 50)
    print("课堂监测简要报告")
    print("=" * 50)
    print(f"总学生数: {report['summary']['total_students']}")
    print(f"出勤学生: {report['summary']['present_students']}")
    print(f"出勤率: {report['summary']['attendance_rate']:.1%}")
    print(f"使用手机学生数: {report['summary']['phone_users_count']}")
    print(f"手机使用总次数: {report['summary']['total_phone_events']}")


if __name__ == "__main__":
    main()