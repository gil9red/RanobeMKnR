__author__ = 'ipetrash'


"""Скрипт, используя данные в _ranobe_/ranobe_info.json (которые получает и сохраняет
скрипт generate_info_ranobe.py), качает с сайта для дальнейшей работы с ними."""


import generate_info_ranobe
import os.path
import sys
import json


if __name__ == '__main__':
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH

    # Если файл по такому пути не существует, завершаем работу скрипта
    if not os.path.exists(ranobe_info_path):
        # TODO: как вариант: если не существует, можно запустить скрипт generate_info_ranobe.
        print("Файл {}, нужный для работы скрипта не существует, для его генерации "
              "нужно использовать скрипт generate_info_ranobe.".format(ranobe_info_path))
        sys.exit()

    # Открываем файл в режиме чтения
    with open(ranobe_info_path, mode='r', encoding='utf8') as f:
        # Десериализация данных в объекты python'а
        ranobe_info = json.load(f)

        print(ranobe_info)