__author__ = 'ipetrash'

"""Скрипт, используя данные в _ranobe_/ranobe_info.json (которые получает и сохраняет
скрипт generate_info_ranobe.py), качает с сайта для дальнейшей работы с ними."""

import os.path
from os import makedirs
import sys
import json

import generate_info_ranobe
from get_volume_info import get_volume_base_page
from grab import Grab

if __name__ == '__main__':
    # Путь к файлу с инфой об ранобе
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH
    # ranobe_dir = generate_info_ranobe.DIR_RANOBE

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

        # Перебор всех томов ранобе
        volumes = ranobe_info.get("volumes")
        for volume in volumes:
            path_dir_volume = volume.get("dir")
            if not os.path.exists(path_dir_volume):
                makedirs(path_dir_volume)

            # Создание папки, в которой будут храниться главы данного тома
            path_dir_chapters = os.path.join(path_dir_volume, "chapters")
            if not os.path.exists(path_dir_chapters):
                makedirs(path_dir_chapters)

            # Перебор списка url глав данного тома
            chapters = volume.get("chapters")
            for ch_url in chapters:
                g = Grab()
                g.go(ch_url)

                file_name = get_volume_base_page(ch_url)
                path_file_chapter = os.path.join(path_dir_chapters, file_name)

                # Получение основного контекста, имеющий номер главы и
                content_text = g.doc.select('//div[@id="mw-content-text"]')

                # Получение названия главы
                name_chapter = g.doc.select('//h2/span[@class="mw-headline"]').text()

                # TODO: учитывать картинки в тексте
                # TODO: учитывать ошибку и подобные ею "Ошибка цитирования Для
                # существующего тега <ref> не найдено соответствующего тега <references/>"
                # TODO: учитывать примечания в тексте
                # TODO: список примечаний можно встретить в конце главы, похоже из-за
                # отсутствия этого списка была та ошибка ""Ошибка цитирования..."

                # Получение и объединение параграфов в единый текст
                chapter_content = '\n'.join(r.text() for r in content_text.select('p'))
                if chapter_content:
                    with open(path_file_chapter, mode='w', encoding='utf8') as f:
                        f.write(name_chapter + '\n\n')
                        f.write(chapter_content)
                else:
                    raise Exception("chapter_content is null")


            #  i   - Начальные иллюстрации
            #  p1  - Вступление
            #  p2  - Пролог
            #  ch% - Глава %
            #  c%  - Глава %
            #  e   - Эпилог
            #  a   - Послесловие
            #  a2  - Запоздавший шедевр
            #  at  - Послесловие команды перевода

            # "ISBN": "978-4048705974",
            # "a": "http://ruranobe.ru/r/mknr/v1/a",
            # "a2": "http://ruranobe.ru/r/mknr/v1/a2",
            # "author": "Сато Цутому",
            # "chapters": [
            #     "http://ruranobe.ru/r/mknr/v1/ch0",
            #     "http://ruranobe.ru/r/mknr/v1/ch1",
            #     "http://ruranobe.ru/r/mknr/v1/ch2",
            #     "http://ruranobe.ru/r/mknr/v1/ch3",
            #     "http://ruranobe.ru/r/mknr/v1/ch4",
            #     "http://ruranobe.ru/r/mknr/v1/ch5"
            # ],
            # "dir": "_ranobe_\\Непутевый ученик в школе магии\\Непутевый ученик в школе магии 1. Зачисление в школу (Часть 1)",
            # "i": "http://ruranobe.ru/r/mknr/v1/i",
            # "illustrator": "Исида Кана",
            # "name": "Непутевый ученик в школе магии 1: Зачисление в школу (Часть 1)",
            # "number": 1,
            # "series": "Непутевый ученик в школе магии",
            # "text": "http://ruranobe.ru/r/mknr/v1/text",
            # "url_cover": "http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png"

    except Exception as err:
        # Выводим ошибку и завершаем работу скрипта
        print(err)
        sys.exit(-1)