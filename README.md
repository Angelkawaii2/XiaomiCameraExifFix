# Xiaomi Leica Camera EXIF Fix / 小米徕卡相机 EXIF 修复

![Lint Test](https://github.com/Angelkawaii2/XiaomiCameraExifFix/actions/workflows/python-package.yml/badge.svg)

一个用于 “修复” 小米徕卡相机在专业模式下 DNG 文件缺少 exif 信息的脚本。      
A script to "FIX" the lacking exif information in DNG files on Xiaomi Leica series cameras.

在小米或红米设备上使用专业模式进行 Raw/UltraRaw 拍摄时，生成的 DNG 文件会缺少以下 EXIF 元数据：
- GPS 位置信息
- 镜头信息
- 焦距信息

缺失这些信息会给使用 Lightroom 等专业软件进行照片管理和输出带来不便。  
此问题已反馈给小米官方，但其工作人员回应表示这是 **“特性”**，不会修复:)  
该脚本通过提取伴生 JPG 文件中的 EXIF 元数据，并将其复制到对应的 DNG 文件中，从而恢复 DNG 文件中应有的拍摄信息。  

> When shooting Raw/UltraRaw photos on Xiaomi/Redmi devices, the DNG files lack EXIF metadata, such as:
> 
> - GPS location
> - Lens information
> - Focal length
> 
> This omission creates significant inconvenience for editing and managing photos in software like Lightroom or similar tools.
> 
> The issue has been reported to Xiaomi's support team, but their response labeled this behavior as a **"feature"**, with no plans for resolution.
> 
> This script extracts EXIF metadata from the accompanying JPG files generated alongside the DNG photos and copies it into the DNG files, effectively restoring the shooting information that should have been present originally.
> 
----

## 支持机型 / Supported Devices

- [ ] Xiaomi 13 / Pro (暂无数据)
- [x] Xiaomi 13 Ultra (2304FPN6DC)
- [x] Xiaomi Mix Fold 3 (2308CPXD0C)
- [x] Xiaomi 14 (23127PN0CC)
- [x] Xiaomi 14 Pro (23116PN5BC)
- [x] Xiaomi 14 Ultra (24031PN0DC)
- [x] Xiaomi Civi 4 Pro (24053PY09C)
- [x] Xiaomi Mix Flip (2405CPX3DC)
- [x] Xiaomi Mix Fold 4 
- [x] Redmi K70 Ultra 
- [x] Xiaomi 15 / Pro
- [x] Xiaomi 15 Ultra

----

## 使用方法 / Usage

### 创建venv /Create venv

> python -m venv ./venv/
> cd venv
> ./activate

#### 安装依赖 / Install Dependencies

> pip install -r requirements.txt

### 命令行参数 / Command Line Arguments

- `--dng-dir`: DNG文件的目录路径。这是一个必需的参数。
- `--jpg-dir`: JPG文件的目录路径。如果未指定，默认为DNG文件的目录路径。
- `--dry-run`: 如果指定，脚本将以演示模式运行，不会对文件进行任何更改。
- `--enable-model-rewrite`: 启用设备型号代码到人类可读型号名称的重写。例如，“Xiaomi 2304FPN6DC”将被重写为“Xiaomi 13
  Ultra”。
- `--delete-trash-jpg`: 在处理后自动删除 raw 模式下的所有伴生 JPG 文件，不包括 ultraraw 。
- `--using-dng-original-exif`: 使用 DNG 照片中已经存在的EXIF，而非JPG的。
- `--support-windows-properties`: 在EXIF数据中添加对 Windows 属性的支持，增强与 Windows 高级照片功能的兼容性。

### 示例 / Examples

1. 推荐备份原始DNG文件 / Backup your .dng files is strongly recommended.
2. 打开终端，运行 / Open the terminal, run :

```shell
python main.py --dng-dir=<path/to/dng/files> --jpg-dir=<path/to/jpg/files> --dry-run
```

## 开源许可证 / License

MIT LICENSE
