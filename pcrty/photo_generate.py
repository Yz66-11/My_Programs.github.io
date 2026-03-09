import cv2
import numpy as np
import os
import albumentations as A


def generate_synthetic_faces(input_base_dir, output_base_dir):
    # 修正参数名：将 pad_mode 改为 mode (albumentations 新版本要求)
    # 模拟侧脸的核心变换
    transforms = {
        "left_side": A.Perspective(scale=(0.08, 0.12), mode=cv2.BORDER_REPLICATE, p=1.0, fit_output=True),
        "right_side": A.Perspective(scale=(0.08, 0.12), mode=cv2.BORDER_REPLICATE, p=1.0, fit_output=True),
        "tilt_up": A.SafeRotate(limit=(15, 20), p=1.0, border_mode=cv2.BORDER_REPLICATE),
        "bright": A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1.0),
        "blur": A.GaussianBlur(blur_limit=(3, 5), p=1.0)
    }

    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # 遍历原始照片目录
    for filename in os.listdir(input_base_dir):
        if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue

        # 解决乱码：获取学生姓名
        student_name = os.path.splitext(filename)[0]
        # 创建学生专属文件夹
        student_output_dir = os.path.join(output_base_dir, student_name)
        if not os.path.exists(student_output_dir):
            os.makedirs(student_output_dir)

        # --- 核心修复：解决中文路径读取 ---
        input_path = os.path.join(input_base_dir, filename)
        img_array = np.fromfile(input_path, dtype=np.uint8)  # 先以字节流读取
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 再解码

        if image is None:
            print(f"无法读取图片: {filename}")
            continue

        # 1. 保存原始正脸 (使用 imencode 处理中文路径)
        def save_chinese_path(img, path):
            ext = os.path.splitext(path)[1]
            res, im_en = cv2.imencode(ext, img)
            if res:
                im_en.tofile(path)

        save_chinese_path(image, os.path.join(student_output_dir, "original.jpg"))

        # 2. 生成并保存合成照片
        for angle_name, aug in transforms.items():
            # 处理右侧视角：先翻转再变换，增加差异度
            if angle_name == "right_side":
                flipped = cv2.flip(image, 1)
                transformed = aug(image=flipped)["image"]
            else:
                transformed = aug(image=image)["image"]

            save_path = os.path.join(student_output_dir, f"{angle_name}.jpg")
            save_chinese_path(transformed, save_path)

        print(f"成功为 [ {student_name} ] 生成多角度合成照片")


if __name__ == "__main__":
    # raw_student_photos 文件夹里放：张三.jpg, 李四.jpg
    # student_photos 文件夹会自动生成：张三/original.jpg, 张三/left_side.jpg ...
    raw_dir = "student_photos"
    target_dir = "photos_dir"

    generate_synthetic_faces(raw_dir, target_dir)