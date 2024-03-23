# Xiaomi Leica Camera EXIF Fix / 小米徕卡相机 EXIF 修复

![Lint Test](https://github.com/Angelkawaii2/XiaomiCameraExifFix/actions/workflows/python-package.yml/badge.svg)

一个用于 “修复” 小米徕卡相机在专业模式下 DNG 文件缺少 exif 信息的脚本。    
A script to “fix” missing exif information in DNG files in Xiaomi Leica series camera pro mode.

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

- [ ] Xiaomi 13 / Pro (暂无数据)
- [x] Xiaomi 13 Ultra (2304FPN6DC)
- [x] Xiaomi Mix Fold 3 (2308CPXD0C)
- [x] Xiaomi 14 (23127PN0CC)
- [x] Xiaomi 14 Pro (23116PN5BC)
- [x] Xiaomi 14 Ultra (24031PN0DC)
- [x] Xiaomi Civi 4 Pro (24053PY09C)

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
- `--support-windows-properties`: 在EXIF数据中添加对Microsoft Windows属性的支持，增强与 Windows 高级照片功能的兼容性。

### 示例 / Examples

1. 推荐备份原始DNG文件 / Backup your .dng files is strongly recommended.
2. 打开终端，运行 / Open the terminal, run :

```shell
python main.py --dng-dir=<path/to/dng/files> --jpg-dir=<path/to/jpg/files> --dry-run
```

## 开源许可证 / License

MIT LICENSE
