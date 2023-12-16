import logging
import os
import sys

import exiftool
from exiftool.exceptions import ExifToolExecuteError

# =============Config=============
DRY_RUN = False
# 重写对应的机型代号到机型的名称
ENABLE_MODEL_REWRITE = True
# 由于raw模式下的jpg存在问题，设为True后将在处理完成后自动删除所有raw的伴生jpg
# 注：ultra-raw 不受影响
DELETE_TRASH_JPG = True

MODEL_CONFIG = {
    "2304FPN6DC": {
        "NAME": "Xiaomi 13 Ultra",
        "LensMap": {
            2.83: "Xiaomi 13 Ultra Front UltraWide Camera",
            2.0: "Xiaomi 13 Ultra Rear UltraWide Camera",  # Sony IMX 858
            2.03: "Xiaomi 13 Ultra Rear UltraWide Camera",  # Sony IMX 858
            8.7: "Xiaomi 13 Ultra Rear Wide Camera",  # Sony IMX 989
            9.87: "Xiaomi 13 Ultra Rear Telephoto Camera",  # Sony IMX 858
            9.9: "Xiaomi 13 Ultra Rear Telephoto Camera",  # Sony IMX 858
            19.4: "Xiaomi 13 Ultra Rear Super Telephoto Camera",  # Sony IMX 858
        }
    },
    "23127PN0CC": {
        "NAME": "Xiaomi 14",
        "LensMap": {
        }
    },
    "23116PN5BC": {
        "NAME": "Xiaomi 14 Pro",
        "LensMap": {
        }
    },
}

# =============Config END=============

DNG_DIR_PATH = ""
JPG_DIR_PATH = ""

basic_tags = ["EXIF:*", "EXIF:GPS*", "XMP:LensModel", "Composite:GPSPosition"]


class Stats:
    pass


stats = Stats()
stats.noGpsInfoCnt = 0  # gps计数
stats.noExistJpgCnt = 0  # 不存在计数
stats.delJpgCnt = 0

logging.basicConfig(level=logging.INFO)


class ColorFilter(logging.Filter):
    COLORS = {
        logging.DEBUG: "\033[0;37m",  # 白色
        logging.INFO: "\033[0;32m",  # 绿色
        logging.WARNING: "\033[0;33m",  # 黄色
        logging.ERROR: "\033[0;31m",  # 红色
        logging.CRITICAL: "\033[0;35m"  # 紫色
    }

    def filter(self, record):
        level = record.levelno
        msg = record.msg
        if level in self.COLORS:
            color = self.COLORS[level]
            record.msg = f"{color}{msg}\033[0m"
        return record


color_filter = ColorFilter()

mainLogger = logging.getLogger("MiFix")
mainLogger.setLevel(level=logging.INFO)
mainLogger.addFilter(color_filter)

exiftoolLogger = logging.getLogger("Exiftool")
exiftoolLogger.setLevel(level=logging.WARN)


def process():
    # 遍历raw_path中所有.dng后缀的文件，存放到列表dng_list中
    dng_list = []

    for file in os.listdir(DNG_DIR_PATH):
        if file.endswith(".dng"):
            dng_list.append(file)

    # 使用exiftool的上下文管理器
    with exiftool.ExifToolHelper(logger=exiftoolLogger) as et:
        # 遍历dng_list中每个文件
        for i, dng_filename in enumerate(dng_list):
            mainLogger.info(
                f"\033[0;35m=============={dng_filename}\033[0;32m(\033[0;37m{i + 1}/\033[0;32m{len(dng_list)})\033["
                f"0;35m==============\033[0m")
            # 获取.dng文件的前缀
            prefix = dng_filename.split(".")[0]
            # 拼接对应的.jpg文件的路径
            jpg_full_path = os.path.join(JPG_DIR_PATH, prefix + ".jpg")
            dng_full_path = os.path.join(DNG_DIR_PATH, dng_filename)

            if not os.path.exists(jpg_full_path):
                mainLogger.warning(f"{jpg_full_path} does not exist! skipped.")
                stats.noExistJpgCnt += 1
                continue

            jpg_exif_info = et.get_tags(jpg_full_path, basic_tags)[0]
            mainLogger.debug(jpg_exif_info)

            exif_model = jpg_exif_info["EXIF:Model"]
            exif_focal = jpg_exif_info["EXIF:FocalLength"]
            rewrite_model = exif_model
            try:
                model_config = MODEL_CONFIG[exif_model]
                try:
                    lens_model = model_config["LensMap"][exif_focal]
                    if ENABLE_MODEL_REWRITE:
                        rewrite_model = model_config["NAME"]
                        mainLogger.debug(f"Model will be rewrote to {rewrite_model}")
                    try:
                        # 将元数据写入图片B，同时保持FileCreateDate和FileModifyDate不变，设置LensModel和Model
                        result_tag_map = {"EXIF:FocalLength": f"'{exif_focal}'", "XMP:LensModel": f"'{lens_model}'",
                                          "EXIF:Model": f"'{rewrite_model}'", "EXIF:ExifVersion": "0220"}
                        # EXIF:FNumber
                        copy_tags = ["EXIF:ApertureValue", "EXIF:FocalLengthIn35mmFormat", "EXIF:Flash",
                                     "EXIF:LightSource", "EXIF:WhiteBalance", "EXIF:ISO", "EXIF:ShutterSpeedValue",
                                     "EXIF:ExposureCompensation",
                                     "EXIF:MeteringMode", "EXIF:GPSLatitude", "EXIF:GPSAltitude",
                                     "EXIF:GPSLatitudeRef", "EXIF:GPSSpeed", "EXIF:GPSAltitudeRef",
                                     "EXIF:GPSProcessingMethod", "EXIF:GPSSpeedRef",
                                     "EXIF:GPSLongitudeRef", "EXIF:GPSTimeStamp", "EXIF:GPSLongitude",
                                     "EXIF:GPSDateStamp"]
                        mainLogger.info(f"Reading exif info from jpg:{jpg_full_path}")

                        tagnofound = []
                        for tag in copy_tags:
                            v = jpg_exif_info.get(tag)
                            if v is not None:
                                result_tag_map[tag] = v
                            else:
                                tagnofound.append(tag)
                                # mainLogger.warning(f"Tag {tag} Not Found!")
                        if tagnofound:
                            mainLogger.warning(f"Some Tag Cannot Be Found: " + " ".join(tagnofound))

                        if "Composite:GPSPosition" not in jpg_exif_info:
                            mainLogger.warning(f"{dng_filename} Gps info not found.", )
                            stats.noGpsInfoCnt += 1

                        mainLogger.debug(result_tag_map)

                        items_ = ["-{}={}".format(k, v) for k, v in result_tag_map.items()]
                        if DRY_RUN:
                            mainLogger.info(f"SIMULATE: {dng_full_path}  " + " ".join(items_))
                        else:
                            mainLogger.info(f"PROCESSING: {dng_full_path}")
                            et.execute("-overwrite_original", "-preserve", "-FileCreateDate<CreateDate",
                                       "-FileModifyDate<ModifyDate",
                                       *items_,
                                       f"-LensModel={lens_model}", f"-Model={rewrite_model}",
                                       dng_full_path)
                        mainLogger.info(f"Write {dng_full_path} Success! ")

                        if DELETE_TRASH_JPG:
                            # dng也要读一下，判断当前的jpg是不是raw
                            dng_exif_info = et.get_tags(dng_full_path, "EXIF:ImageDescription")[0]
                            is_trash_jpg = dng_exif_info.get("EXIF:ImageDescription") == "raw"
                            if is_trash_jpg:
                                if not DRY_RUN:
                                    os.remove(jpg_full_path)
                                mainLogger.warning(f"Trash jpg: {jpg_full_path} has been removed.")
                                stats.delJpgCnt += 1
                    except ExifToolExecuteError as e:
                        mainLogger.error(e.stderr)
                        mainLogger.error(e.stdout)
                        raise e
                except KeyError:
                    raise RuntimeError(
                        f"Error: Unknown Focal:{exif_focal} in MODEL_CONFIG: {model_config['LensMap']}")
            except KeyError:
                raise RuntimeError(f"Error: Unsupported Device: {exif_model}")

    mainLogger.info("===============Task Completed！==============")
    mainLogger.info(f"NoGpsPhotoCnt: {stats.noGpsInfoCnt}")
    mainLogger.info(f"NoJPGPhotoCnt: {stats.noExistJpgCnt}")
    mainLogger.info(f"DelTrashJPGCnt: {stats.delJpgCnt}")
    mainLogger.info("===============XiaomiCameraExifFix==============")


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        mainLogger.info("""
Usage:
main.py <dng_files_path> [jpg_files_path] 
        """)
        exit(1)

    DNG_DIR_PATH = sys.argv[1]
    if len(sys.argv) == 2:
        JPG_DIR_PATH = DNG_DIR_PATH
    else:
        JPG_DIR_PATH = sys.argv[2]

    # do Logic
    mainLogger.info(f"""
    DNG_Path: {DNG_DIR_PATH}
    JPG_Path: {JPG_DIR_PATH}
    """)
    process()
