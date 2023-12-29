# Xiaomi 13/14 Camera EXIF Fix / 小米13/14 相机 EXIF 修复

![Lint Test](https://github.com/Angelkawaii2/XiaomiCameraExifFix/actions/workflows/python-package.yml/badge.svg)

一个用于 “修复” 小米13/14 相机专业模式下 DNG 文件缺少 exif 信息的脚本。    
A script to “fix” missing exif information in DNG files in Xiaomi 13/14 series camera pro mode.

在 小米13/14 上使用 专业模式 进行 Raw / UltraRaw 摄影时，dng 文件会缺少 GPS位置、镜头、焦距等 EXIF 信息，这会给使用
Lightroom 等软件输出和管理带来很多不便。  
此问题已向小米官方反馈，但官方员工表示此问题不会得到修复。  
因此，该脚本从 DNG 照片伴生的 jpg 文件中复制 EXIF 信息，使得 DNG 能够“保留”原本应该存在的拍摄信息。

When using Raw/UltraRaw camera mode in Pro-mode on the Xiaomi 13/14 series, the dng file will lack EXIF information
such as GPS location, lens, focal length, etc., which will cause a lot of inconvenience for management.   
This issue has been reported to Xiaomi official, but official said this issue will not be fixed.
Therefore, the script copies the EXIF information from the jpg file that accompanies the DNG photo,
allowing the DNG to "preserve" the shooting information that should otherwise be there.


----

## 支持机型 / Supported Devices
- [ ] Xiaomi 13 / Pro (No FocalLens)
- [x] Xiaomi 13 Ultra
- [x] Xiaomi 14 
- [x] Xiaomi 14 Pro 

----

## 使用方法 / Usage

### 前置条件 / Precondition

- Python 3.12 (已测试 / Tested)

1. 推荐备份原始DNG文件 / Backup your .dng files is strongly recommended.
2. 在运行之前，您可以编辑 ``main.py`` 中的设置项，根据需求开启或关闭。/ Before running this script, you can edit the settings in ``main.py`` and change the settings according to your needs.
3. 打开终端，运行 / Open the terminal, run :

#### 创建venv 
> python -m venv ./venv/
> cd venv
> ./activate
#### 安装依赖
> pip install -r requirements.txt
#### 运行
> python main.py <dng_dir_path> [jpg_dir_path]

### 开源许可证 / License

MIT LICENSE
