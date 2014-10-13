__author__ = 'ipetrash'


"""Скрипт парсит сайт ранобе http://ruranobe.ru/r/mknr, вытаскивает
информацию о ранобе, томах и главах, после ее сохраняет."""


import get_ranobe_info
import get_volume_info
import json
from urllib.parse import urljoin
import os.path
from os import makedirs


if __name__ == '__main__':
    ranobe = get_ranobe_info.ranobe_info()

    url = ranobe["url"]
    name_ranobe = ranobe["name"]
    annotation = ranobe["annotation"]
    list_volumes = ranobe["list_volumes"]

    # В папке с скриптом создаем папку c названием name_ranobe
    dir_ranobe = "_ranobe_"
    if not os.path.exists(dir_ranobe):
        makedirs(dir_ranobe)

    author = None
    series = None
    illustrator = None

    print("Название: '{}'".format(name_ranobe))
    print("\nАннотации:\n'{}'".format(annotation))
    print("\nТома ({}):".format(len(list_volumes)))

    volumes = list()
    for n, v in enumerate(list_volumes, 1):
        print("Глава {}:".format(n))

        # Соединение адреса к главной странице ранобе и относительной ссылки к тОму
        url_volume = urljoin(url, v.attr('href'))

        volume_info = get_volume_info.volume_info(url_volume, url)
        if volume_info:
            # Номер тома в серии
            volume_info["number"] = n

            # Добавляем том к списку томов
            volumes.append(volume_info)

            # # Создание папки тома ранобе
            # volume_name = volume_info.get("name").replace(':', '.')
            # dir_volume_ranobe = os.path.join(dir_ranobe, volume_name)
            # if not os.path.exists(dir_volume_ranobe):
            #     makedirs(dir_volume_ranobe)

            if not author:
                author = volume_info.get("author")

            if not series:
                series = volume_info.get("series")

            if not illustrator:
                illustrator = volume_info.get("illustrator")

            print("  Адрес тома: {}".format(url_volume))
            print("  ALL: {}".format(volume_info))
            print("    Название:    {}".format(volume_info.get("name")))
            print("    Серия:       {}".format(series))
            print("    Автор:       {}".format(author))
            print("    Иллюстратор: {}".format(illustrator))
            print("    ISBN:        {}".format(volume_info.get("ISBN")))
            print("    Обложка:     {}".format(volume_info.get("url_cover")))
            print("    Содержание:")
            print("        Начальные иллюстрации: {}".format(volume_info.get("i")))
            print("        Вступление: {}".format(volume_info.get("p1")))
            print("        Пролог: {}".format(volume_info.get("p2")))
            print("        Главы:")
            for i, ch in enumerate(volume_info.get("chapters"), 1):
                print("            {}. '{}'".format(i, ch))
            print("        Эпилог: {}".format(volume_info.get("e")))
            print("        Послесловие: {}".format(volume_info.get("a")))
            print("        Запоздавший шедевр: {}".format(volume_info.get("a2")))
        else:
            print("Неудача с томом: {}".format(url_volume))
        print()

    # Создадим файл, содержащий описание к ранобе: название, автор, аннотацию и т.п.
    ranobe_info_path = os.path.join(dir_ranobe, 'ranobe_info')
    with open(ranobe_info_path, mode='w', encoding='utf8') as f:
        dump_data = {
            "name": name_ranobe,
            "author": author,
            "illustrator": illustrator,
            "series": series,
            "annotation": annotation,
            "url": url,
            "volumes": volumes,
        }
        json.dump(dump_data, f, ensure_ascii=False, sort_keys=True, indent=4)
