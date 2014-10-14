__author__ = 'ipetrash'


"""Скрипт, используя данные в _ranobe_/ranobe_info.json (которые получает и сохраняет
скрипт generate_info_ranobe.py), качает с сайта для дальнейшей работы с ними."""


import generate_info_ranobe
import os.path
import sys
import json


if __name__ == '__main__':
    # Путь к файлу с инфой об ранобе
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH

    try:
        # Если файла по такому пути не существует, завершаем работу скрипта
        if not os.path.exists(ranobe_info_path):
            raise Exception("Файл {} не существует".format(ranobe_info_path))

        ranobe_info = None

        # Открываем файл в режиме чтения
        with open(ranobe_info_path, mode='r', encoding='utf8') as f:
            # Десериализация данных в объекты python'а
            try:
                ranobe_info = json.load(f)
            except ValueError as err:
                raise Exception("Файл {} испорчен: {}".format(ranobe_info_path, err))


        print(ranobe_info)
        print("\nНазвание: '{}'".format(ranobe_info.get("name")))
        print("Автор: '{}'".format(ranobe_info.get("author")))
        print("Иллюстратор: '{}'".format(ranobe_info.get("illustrator")))
        print("Серия: '{}'".format(ranobe_info.get("series")))
        print("Аннотации:\n'{}'".format(ranobe_info.get("annotation")))


    except Exception as err:
        # Выводим ошибку и завершаем работу скрипта
        print(err)
        sys.exit(-1)