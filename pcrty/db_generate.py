import os
import cv2
import numpy as np
from deepface import DeepFace


def register_incremental(input_dir="photos_dir", db_save_path="student_db.npy"):
    model_name = "ArcFace"
    # 1. 加载现有数据库（增量更新核心）
    if os.path.exists(db_save_path):
        try:
            known_db = np.load(db_save_path, allow_pickle=True).item()
            print(f"加载现有资料成功，已注册人数: {len(known_db)}")
        except Exception as e:
            print(f"警告：读取资料库失败 ({e})，将创建新数据库。")
            known_db = {}
    else:
        known_db = {}
        print("未找到现有资料库，将重新开始注册。")

    input_dir = os.path.abspath(input_dir)
    if not os.path.exists(input_dir):
        print(f"错误：找不到目录 -> {input_dir}")
        return

    new_registers = 0

    # 2.遍历目录
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue

            student_name = os.path.splitext(filename)[0]

            # --- 增量检查：如果姓名已在库中，跳过 ---
            if student_name in known_db:
                # print(f"跳过: {student_name} (已在资料库中)")
                continue

            img_path = os.path.join(root, filename)
            print(f"发现新学生，正在处理: {student_name} ...", end=" ", flush=True)

            try:
                img_array = np.fromfile(img_path, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if img is None:
                    print("读取失败 ")
                    continue

                # 3. 提取特征（支持原图与镜像融合）
                variants = [img, cv2.flip(img, 1)]
                embs = []

                for v_img in variants:
                    res = DeepFace.represent(
                        v_img,
                        model_name=model_name,
                        enforce_detection=True,
                        detector_backend='opencv'
                    )
                    if res:
                        v = np.array(res[0]["embedding"], dtype=np.float32)
                        embs.append(v / np.linalg.norm(v))

                if embs:
                    mean_v = np.mean(embs, axis=0)
                    known_db[student_name] = mean_v / np.linalg.norm(mean_v)
                    new_registers += 1
                    print("成功")
                else:
                    print("未检测到人脸")

            except Exception as e:
                print(f"异常: {str(e)}")

    # 4. 保存更新后的数据库
    if new_registers > 0:
        np.save(db_save_path, known_db)
        print(f"\n增量更新完成！本次新增 {new_registers} 位学生，总数为 {len(known_db)}。")
    else:
        print("\n扫描结束，沒有发现新学生照片。")


if __name__ == "__main__":
    # 资料夹名称与现有目录保持一致
    register_incremental(input_dir="photos_dir")