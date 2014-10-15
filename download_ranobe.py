__author__ = 'ipetrash'

"""Скрипт, используя данные в _ranobe_/ranobe_info.json (которые получает и сохраняет
скрипт generate_info_ranobe.py), качает с сайта для дальнейшей работы с ними."""

import os.path
from os import makedirs
import sys
import json

import generate_info_ranobe


if __name__ == '__main__':
    # Путь к файлу с инфой об ранобе
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH
    ranobe_dir = generate_info_ranobe.DIR_RANOBE

    try:
        # Если файла по такому пути не существует, завершаем работу скрипта
        if not os.path.exists(ranobe_info_path):
            raise Exception("Файл {} не существует".format(ranobe_info_path))

        ranobe_info = None

        # Открываем файл в режиме чтения
        with open(ranobe_info_path, mode='r', encoding='utf8') as f:
            try:
                # Десериализация данных в объекты python'а
                ranobe_info = json.load(f)

            except ValueError as err:
                raise Exception("Файл {} испорчен: {}".format(ranobe_info_path, err))

        print(ranobe_info)

        # # Создадим папку с таким же названием, как у ранобе
        # name = ranobe_info.get("name")
        # path_dir_ranobe = os.path.join(ranobe_dir, name)
        # if not os.path.exists(path_dir_ranobe):
        # makedirs(path_dir_ranobe)

        # Перебор всех томов ранобе
        volumes = ranobe_info.get("volumes")
        for volume in volumes:
            path_dir_volume = volume.get("dir")
            if not os.path.exists(path_dir_volume):
                makedirs(path_dir_volume)


                # print("\nНазвание: '{}'".format(name))
                # print("Автор: '{}'".format(ranobe_info.get("author")))
                # print("Иллюстратор: '{}'".format(ranobe_info.get("illustrator")))
                # print("Серия: '{}'".format(ranobe_info.get("series")))
                # print("Аннотации:\n'{}'".format(ranobe_info.get("annotation")))


    except Exception as err:
        # Выводим ошибку и завершаем работу скрипта
        print(err)
        sys.exit(-1)