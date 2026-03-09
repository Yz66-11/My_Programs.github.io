import os
import cv2
import numpy as np
from deepface import DeepFace


def register_incremental(input_dir="photos_dir", db_save_path="student_db.npy"):
    model_name = "ArcFace"
    # 1. 加載現有數據庫（增量更新核心）
    if os.path.exists(db_save_path):
        try:
            known_db = np.load(db_save_path, allow_pickle=True).item()
            print(f"加載現有資料庫成功，已註冊人數: {len(known_db)}")
        except Exception as e:
            print(f"警告：讀取舊資料庫失敗 ({e})，將創建新庫。")
            known_db = {}
    else:
        known_db = {}
        print("未找到現有資料庫，將從零開始註冊。")

    input_dir = os.path.abspath(input_dir)
    if not os.path.exists(input_dir):
        print(f"錯誤：找不到目錄 -> {input_dir}")
        return

    new_registers = 0

    # 2. 遍歷目錄
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue

            student_name = os.path.splitext(filename)[0]

            # --- 增量檢查：如果姓名已在庫中，則跳過 ---
            if student_name in known_db:
                # print(f"跳過: {student_name} (已在資料庫中)")
                continue

            img_path = os.path.join(root, filename)
            print(f"發現新學員，正在處理: {student_name} ...", end=" ", flush=True)

            try:
                img_array = np.fromfile(img_path, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if img is None:
                    print("讀取失敗")
                    continue

                # 3. 提取特徵（支持原圖與鏡像融合）
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
                    print("未檢測到人臉")

            except Exception as e:
                print(f"異常: {str(e)}")

    # 4. 保存更新後的特徵庫
    if new_registers > 0:
        np.save(db_save_path, known_db)
        print(f"\n增量更新完成！本次新增 {new_registers} 位學生，總數為 {len(known_db)}。")
    else:
        print("\n掃描結束，沒有發現新學生照片。")


if __name__ == "__main__":
    # 確保資料夾名稱與你的環境一致
    register_incremental(input_dir="photos_dir")