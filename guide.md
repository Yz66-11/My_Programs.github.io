# 环境配置教程

## 选择开发方式

- **VS Code + Anaconda**
- **PyCharm + Anaconda（推荐）**

## 一、安装开发环境（以下所有内容以PyCharm环境为例）

1. 前往PyCharm官网下载社区版[https://www.jetbrains.com/zh-cn/pycharm/](https://www.jetbrains.com/zh-cn/pycharm/)
2. 下载Anaconda[https://www.anaconda.com/download](https://www.anaconda.com/download)
>详细安装教程可参考以下文章https://blog.csdn.net/m0_66047447/article/details/141110995?ops_request_misc=elastic_search_misc&request_id=ddfbb7d460f5ee22f4ad96db55205f90&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-141110995-null-null.142^v102^pc_search_result_base3&utm_term=anaconda%E5%AE%89%E8%A3%85&spm=1018.2226.3001.4187
3. 安装完成后创建自己的虚拟环境即可
```javascript
conda create -n myenv(此处环境名可以自定义) python 3.9.10
```
4. 激活创建好的虚拟环境
```javascript
conda activate myenv
```
   在该环境中安装Pytorch,先进入设备管理器，查看显示适配器信息
   [![](1)](/Gd1.png)
   如有独立显卡，请参照以下文章安装CUDA和Cudnn
   https://blog.csdn.net/weixin_52677672/article/details/135853106?ops_request_misc=elastic_search_misc&request_id=6885b12515e521efe810508268a91565&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-135853106-null-null.142^v102^pc_search_result_base3&utm_term=cuda%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B&spm=1018.2226.3001.4187
> 如果没有独立显卡，请跳过此步骤
5. 按照教程安装完成后，确保验证成功，安装对应版本的Pytorch
   https://pytorch.org/get-started/locally/
   选择Windows版本下pip安装包，并选择符合要求的CUDA版本，CPU请直接选择CPU版本，之后复制给出的下载命令，重新回到之前的虚拟环境中运行该命令
> 以GPU的12.6版本为例

 ```javascript
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```
安装完成后以管理员身份运行cmd，进入python环境，输入import torch，未出现报错信息则说明安装成功
## 二、构建项目文件结构
 #####1. 在根目录下创建运行文件夹Runs
 #####2.该文件夹下创建train和val，用于存放训练集和验证集
 #####3.train和val文件夹中分别创建images和labels文件夹，分别存放图片数据和标签数据
 #####4.（可选）将yolov8n.pt训练文件下载到根目录中
 #####5.复制.py文件到根目录下，尝试运行，如果提示缺少依赖，请自行在终端中使用pip命令进行补充安装

 >请参考以下文章，创建新的虚拟环境后配置labelimg环境，为后续标注数据集做准备。
 
   https://blog.csdn.net/weixin_65829275/article/details/146942133?ops_request_misc=elastic_search_misc&request_id=b8c6b41e83fb43f9ce9833be361aaf92&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-146942133-null-null.142^v102^pc_search_result_base3&utm_term=labelimg%E5%AE%89%E8%A3%85&spm=1018.2226.3001.4187
**祝您使用愉快！**
