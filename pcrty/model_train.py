#model_train.py
from ultralytics import YOLO

if __name__ == "__main__":
    """
    introduction:
    1. 确保数据集目录结构如下:
       dataset/
         ├── images/
         │   ├── train/  # 训练图片
         │   └── val/    # 验证图片
         ├── labels/
         │   ├── train/  # 训练标签
         │   └── val/    # 验证标签
         └── dataset.yaml # 数据集配置文件

    2. dataset.yaml内容示例:
        path: /path/to/dataset
        train: images/train
        val: images/val
        nc: 2  # 类别数量
        names: ['face', 'phone']  # 类别名称
    """

    # 加载预训练模型
    model = YOLO('yolov8n.pt')

    # 训练模型
    model.train(
        data='info.yaml',  # 数据集配置文件路径
        epochs=500,  # 训练轮数
        imgsz=640,  # 图片尺寸
        batch=16,  # 批次大小
        #lr0=0.01,  # 学习率
        save=True,  # 保存模型
        project='runs/train_result',  # 保存目录
        name='class_monitor',  # 实验名称
        verbose=True  # 显示训练信息
    )

    print("训练完成！最佳模型保存在: runs/train/class_monitor/weights/best.pt")
