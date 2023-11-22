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
DELETE_TRASH_JPG = False

MODEL_CONFIG = {
    "2304FPN6DC": {
        "NAME": "Xiaomi 13 Ultra",
        "LensMap": {
            2.83: "Xiaomi 13 Ultra Front UltraWide Camera",
            2.0: "Xiaomi 13 Ultra Rear UltraWide Camera",  # Sony IMX 858
            8.7: "Xiaomi 13 Ultra Rear Wide Camera",  # Sony IMX 989
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

logging.basicConfig(level=logging.INFO)


def process():
    # 遍历raw_path中所有.dng后缀的文件，存放到列表dng_list中
    dng_list = []

    for file in os.listdir(DNG_DIR_PATH):
        if file.endswith(".dng"):
            dng_list.append(file)

    # 使用exiftool的上下文管理器
    with exiftool.ExifToolHelper(logger=logging) as et:
        # 遍历dng_list中每个文件
        for i, dng_filename in enumerate(dng_list):
            logging.info(f"=============={dng_filename}({i + 1}/{len(dng_list)})==============")
            # 获取.dng文件的前缀
            prefix = dng_filename.split(".")[0]
            # 拼接对应的.jpg文件的路径
            jpg_full_path = os.path.join(JPG_DIR_PATH, prefix + ".jpg")
            dng_full_path = os.path.join(DNG_DIR_PATH, dng_filename)

            if not os.path.exists(jpg_full_path):
                logging.warning(f"{jpg_full_path} does not exist! skipped.")
                continue

            jpg_exif_info = et.get_tags(jpg_full_path, basic_tags)[0]
            logging.debug(jpg_exif_info)

            exif_model = jpg_exif_info["EXIF:Model"]
            exif_focal = jpg_exif_info["EXIF:FocalLength"]
            rewrite_model = exif_model
            try:
                model_config = MODEL_CONFIG[exif_model]
                try:
                    lens_model = model_config["LensMap"][exif_focal]
                    if ENABLE_MODEL_REWRITE:
                        rewrite_model = model_config["NAME"]
                        logging.debug(f"Model will be rewrote to {rewrite_model}")
                    try:
                        # 将元数据写入图片B，同时保持FileCreateDate和FileModifyDate不变，设置LensModel和Model
                        result_tag_map = {"EXIF:FocalLength": f"'{exif_focal}'", "XMP:LensModel": f"'{lens_model}'",
                                          "EXIF:Model": f"'{rewrite_model}'", "EXIF:ExifVersion": "0220"}
                        # EXIF:FNumber
                        copy_tags = ["EXIF:ApertureValue", "EXIF:FocalLengthIn35mmFormat", "EXIF:Flash",
                                     "EXIF:LightSource", "EXIF:WhiteBalance", "EXIF:ISO", "EXIF:ShutterSpeedValue",
                                     "EXIF:ExposureCompensation"
                                     "EXIF:ExposureMode", "EXIF:MeteringMode", "EXIF:GPSLatitude", "EXIF:GPSAltitude",
                                     "EXIF:GPSLatitudeRef", "EXIF:GPSSpeed", "EXIF:GPSAltitudeRef",
                                     "EXIF:GPSProcessingMethod", "EXIF:GPSSpeedRef",
                                     "EXIF:GPSLongitudeRef", "EXIF:GPSTimeStamp", "EXIF:GPSLongitude",
                                     "EXIF:GPSDateStamp"]
                        for tag in copy_tags:
                            v = jpg_exif_info.get(tag)
                            if v is not None:
                                result_tag_map[tag] = v
                            else:
                                logging.warning(f"Tag {tag} can not be found in jpg file.")
                        if "Composite:GPSPosition" not in jpg_exif_info:
                            logging.warning(f"{dng_filename} Gps info not found.", )

                        logging.debug(result_tag_map)

                        items_ = ["-{}={}".format(k, v) for k, v in result_tag_map.items()]
                        if DRY_RUN:
                            logging.info(f"SIMULATE: {dng_full_path} {items_}")
                        else:
                            print(f"PROCESSING: {dng_full_path}")
                            et.execute("-overwrite_original", "-preserve", "-FileCreateDate<CreateDate",
                                       "-FileModifyDate<ModifyDate",
                                       *items_,
                                       f"-LensModel={lens_model}", f"-Model={rewrite_model}",
                                       dng_full_path)
                        print(f"Write {dng_full_path} Success! ")

                        if DELETE_TRASH_JPG:
                            # dng也要读一下，判断当前的jpg是不是raw
                            dng_exif_info = et.get_tags(dng_full_path, "EXIF:ImageDescription")[0]
                            is_trash_jpg = dng_exif_info.get("EXIF:ImageDescription") == "raw"
                            if is_trash_jpg:
                                if not DRY_RUN:
                                    os.remove(jpg_full_path)
                                logging.info(f"Trash jpg: {jpg_full_path} has been removed.")
                    except ExifToolExecuteError as e:
                        print(e.stderr)
                        print(e.stdout)
                        raise e
                except KeyError:
                    raise RuntimeError(
                        f"Error: Unknown Focal:{exif_focal} in MODEL_CONFIG: {model_config['LensMap']}")
            except KeyError:
                raise RuntimeError(f"Error: Unsupported Device: {exif_model}")


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("""
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
    logging.info(f"""
    DNG_Path: {DNG_DIR_PATH}
    JPG_Path: {JPG_DIR_PATH}
    """)
    process()
