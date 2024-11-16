import os
import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread

def get_file_size(file_path):
    size = os.path.getsize(file_path)
    return size / 1024  # Возвращает размер в КБ

def get_exif_data(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)
    exif_data = {}
    gps_data = {}

    for tag, value in tags.items():
        tag_name = TAGS.get(tag, tag)
        if tag.startswith("GPS"):
            gps_tag_name = GPSTAGS.get(tag, tag)
            gps_data[gps_tag_name] = value
        else:
            exif_data[tag_name] = value

    exif_data['GPSInfo'] = gps_data if gps_data else None
    return exif_data

def get_gps_coordinates(gps_info):
    if not gps_info:
        return None, None

    def convert_to_degrees(value):
        d, m, s = value.values
        return d + (m / 60.0) + (s / 3600.0)

    try:
        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            lon = convert_to_degrees(gps_info['GPSLongitude'])

            if gps_info.get('GPSLatitudeRef') and gps_info['GPSLatitudeRef'].values != 'N':
                lat = -lat
            if gps_info.get('GPSLongitudeRef') and gps_info['GPSLongitudeRef'].values != 'E':
                lon = -lon
            return lat, lon
    except Exception as e:
        print(f"Ошибка обработки GPS: {e}")
    return None, None

def print_exif_data(exif_data):
    print("\n[Основные метаданные]")
    keys = {
        'Make': 'Производитель камеры',
        'Model': 'Модель камеры',
        'Software': 'Версия ПО камеры',
        'DateTimeOriginal': 'Дата съемки',
        'ExposureTime': 'Выдержка',
        'FNumber': 'Диафрагма',
        'ISOSpeedRatings': 'ISO',
        'FocalLength': 'Фокусное расстояние',
        'Orientation': 'Ориентация',
        'XResolution': 'Разрешение по X',
        'YResolution': 'Разрешение по Y',
        'WhiteBalance': 'Баланс белого',
        'ExposureMode': 'Режим экспозиции',
        'Flash': 'Тип вспышки',
        'SceneType': 'Тип сцены',
        'MeteringMode': 'Режим замера экспозиции',
        'ColorSpace': 'Цветовое пространство',
        'Model': 'Модель устройства',
        'Make': 'Производитель устройства',
    }

    for tag, description in keys.items():
        value = exif_data.get(tag, None)
        if value:
            print(f"{description}: {value}")
        else:
            print(f"{description}: Данные не найдены")

    print("\n[Данные GPS]")
    gps_info = exif_data.get('GPSInfo', {})
    if gps_info:
        for tag, value in gps_info.items():
            print(f"{tag}: {value}")
    else:
        print("GPS данные: Не найдены")

def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        return img.size  # (width, height)

def get_color_profile(image_path):
    with Image.open(image_path) as img:
        try:
            return img.info.get('icc_profile', None)
        except KeyError:
            return None

def get_image_format(image_path):
    with Image.open(image_path) as img:
        return img.format  # Формат изображения (JPEG, PNG, и т. д.)

def main():
    image_name = input("Введите имя изображения (с расширением): ")
    image_path = os.path.join(os.getcwd(), image_name)

    if not os.path.exists(image_path):
        print(f"Файл {image_name} не найден в текущей папке.")
        return

    print(f"\nОбработка файла: {image_name}")
    
    try:
        file_size = get_file_size(image_path)
        print(f"Размер файла: {file_size:.2f} KB")
        
        exif_data = get_exif_data(image_path)

        date_taken = exif_data.get('DateTimeOriginal', 'Не указано')
        print(f"Дата съемки: {date_taken}")

        gps_coordinates = get_gps_coordinates(exif_data.get('GPSInfo', None))
        if gps_coordinates != (None, None):
            print(f"GPS Координаты: {gps_coordinates[0]:.6f}, {gps_coordinates[1]:.6f}")
        else:
            print("GPS Координаты: Не найдены")

        image_width, image_height = get_image_dimensions(image_path)
        print(f"Размер изображения: {image_width}x{image_height} пикселей")

        color_profile = get_color_profile(image_path)
        if color_profile:
            print(f"Цветовой профиль изображения: Содержит ICC профиль")
        else:
            print(f"Цветовой профиль изображения: Не найден")

        image_format = get_image_format(image_path)
        print(f"Формат изображения: {image_format}")

        print_exif_data(exif_data)

    except Exception as e:
        print(f"Ошибка обработки файла: {e}")

if __name__ == "__main__":
    main()