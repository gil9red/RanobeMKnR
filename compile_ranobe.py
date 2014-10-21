__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""

import generate_info_ranobe
import os.path
import sys

if __name__ == '__main__':
    # Путь к папке с генерированной информацией
    ranobe_dir = generate_info_ranobe.DIR_RANOBE

    if not os.path.exists(ranobe_dir):
        print('{} не существует.'.format(ranobe_dir))
        sys.exit(-1)

    # TODO: имя файла с ранобе нужно такое же как и название ранобе
    # Название файла ранобе
    name_ranobe_fb2 = 'ranobe.fb2'

    # Путь к файлу ранобе
    path_ranobe_fb2 = os.path.join(ranobe_dir, name_ranobe_fb2)

    # Открытие и перезапись файла ранобк
    with open(path_ranobe_fb2, mode='w', encoding='utf8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        f.write('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" '
                'xmlns:xlink="http://www.w3.org/1999/xlink">' + '\n')
        f.write('<body>' + '<p>' + 'Hello мир!' + '</p>' + '</body>')
        f.write('</FictionBook>')