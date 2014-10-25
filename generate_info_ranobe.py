__author__ = 'ipetrash'

"""Скрипт парсит сайт ранобе http://ruranobe.ru/r/mknr, вытаскивает
информацию о ранобе, томах и главах, после ее сохраняет."""

import json
from urllib.parse import urljoin
import os.path
from os import makedirs

import get_ranobe_info
import get_volume_info


DIR_RANOBE = "_ranobe_"
RANOBE_INFO_PATH = os.path.join(DIR_RANOBE, 'ranobe_info.json')

if __name__ == '__main__':
    ranobe = get_ranobe_info.ranobe_info()

    url = ranobe["url"]
    ranobe_name = ranobe["name"]
    annotation = ranobe["annotation"]
    list_volumes = ranobe["list_volumes"]

    # В папке с скриптом создаем папку c названием DIR_RANOBE
    if not os.path.exists(DIR_RANOBE):
        makedirs(DIR_RANOBE)

    author = None
    series = None
    illustrator = None

    print("Название: '{}'".format(ranobe_name))
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

            if not author:
                author = volume_info.get("author")

            if not series:
                series = volume_info.get("series")

            if not illustrator:
                illustrator = volume_info.get("illustrator")

            # Список глав тома
            chapters = volume_info.get("pages").get("chapters")

            # Словарь страниц тома, которые не относятся к главам: послесловие, пролог, и т.д.
            other_pages = volume_info.get("pages").get("other")

            print("  Адрес тома: {}".format(url_volume))
            # print("  ALL: {}".format(volume_info))
            print("    Название:    {}".format(volume_info.get("name")))
            print("    Серия:       {}".format(series))
            print("    Автор:       {}".format(author))
            print("    Иллюстратор: {}".format(illustrator))
            print("    ISBN:        {}".format(volume_info.get("ISBN")))
            print("    Команда:     {}".format(volume_info.get("translation").get("team")))
            print("    Перевод:     {}".format(', '.join(volume_info.get("translation").get('translators'))))
            print("    Обложка:     {}".format(volume_info.get("url_cover")))
            print("    Содержание:")
            print("        Начальные иллюстрации: {}".format(other_pages.get("i")))
            print("        Вступление: {}".format(other_pages.get("p1")))
            print("        Пролог: {}".format(other_pages.get("p2")))
            print("        Главы:")
            for i, ch in enumerate(chapters, 1):
                ch_url, ch_name = ch
                print("            {}. '{}': {}".format(i, ch_name, ch_url))
            print("        Эпилог: {}".format(other_pages.get("e")))
            print("        Послесловие: {}".format(other_pages.get("a")))
            print("        Запоздавший шедевр: {}".format(other_pages.get("a2")))
        else:
            print("Неудача с томом: {}".format(url_volume))

        print()

    # Создадим файл, содержащий описание к ранобе: название, автор, аннотацию и т.п.
    with open(RANOBE_INFO_PATH, mode='w', encoding='utf8') as f:
        dump_data = {
            "name": ranobe_name,
            "author": author,
            "illustrator": illustrator,
            "series": series,
            "annotation": annotation,
            "url": url,
            "volumes": volumes,
        }
        json.dump(dump_data, f, ensure_ascii=False, sort_keys=True, indent=4)