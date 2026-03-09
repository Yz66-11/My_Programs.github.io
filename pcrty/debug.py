import os
import sys
import cv2
import numpy as np


def path_diagnostic_clean(folder_name="origin_photos"):
    # 1. 獲取絕對路徑
    current_dir = os.getcwd()
    target_dir = os.path.join(current_dir, folder_name)

    print("--- Path Diagnostic Start ---")
    print(f"Current Working Directory (CWD): {current_dir}")
    print(f"Target Directory Path: {target_dir}")

    # 2. 檢查目錄是否存在
    exists = os.path.exists(target_dir)
    print(f"Directory Exists: {exists}")

    if not exists:
        print(f"Error: Folder '{folder_name}' not found in the current directory.")
        return

    # 3. 列出目錄下所有文件
    try:
        all_content = os.listdir(target_dir)
        print(f"Total items found: {len(all_content)}")
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return

    if len(all_content) == 0:
        print("Warning: The directory is empty.")
        return

    # 4. 詳細檢查每個文件
    print("\n--- File List Details ---")
    valid_images = []
    for item in all_content:
        # 獲取後綴並轉為小寫
        ext = os.path.splitext(item)[1].lower()
        # 判斷是否為常見圖片格式
        is_img = ext in ['.jpg', '.png', '.jpeg', '.bmp']

        print(f"Filename: {item} | Extension: {ext} | Is Image: {is_img}")

        if is_img:
            valid_images.append(item)

    # 5. 嘗試讀取第一張圖片進行中文兼容性測試
    if valid_images:
        test_img_name = valid_images[0]
        test_img_path = os.path.join(target_dir, test_img_name)
        print(f"\n--- Testing Image Read: {test_img_name} ---")
        try:
            # 使用 numpy 讀取以支持中文路徑
            img_array = np.fromfile(test_img_path, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:
                print(f"Success: Image read correctly. Resolution: {img.shape}")
            else:
                print("Failed: OpenCV could not decode the image data.")
        except Exception as e:
            print(f"Exception during read: {e}")
    else:
        print("\nConclusion: Files exist but none match .jpg, .png, or .jpeg extensions.")
        print("Suggestion: Check if file extensions are hidden or if they are typed incorrectly.")


if __name__ == "__main__":
    # 如果你的資料夾名稱不同，請在此處修改
    path_diagnostic_clean("photos_dir")