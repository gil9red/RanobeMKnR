from get_ranobe_info import ranobe_info

__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""

import os.path
# import sys
import json

import generate_info_ranobe


# http://www.fictionbook.org/index.php/Описание_формата_FB2_от_Sclex
# http://www.fictionbook.org/index.php/Элементы_стандарта_FictionBook

if __name__ == '__main__':
    # Путь к папке с генерированной информацией
    ranobe_dir = generate_info_ranobe.DIR_RANOBE

    # Путь к файлу с инфой об ранобе
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH

    ranobe_info = None

    # Открываем файл в режиме чтения
    with open(ranobe_info_path, mode='r', encoding='utf8') as f:
        # Десериализация данных в объекты python'а
        ranobe_info = json.load(f)

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
        f.write('<description>')
        f.write('<title-info>')

        f.write('<book-title>' + ranobe_info['name'] + '</book-title>')

        f.write('<author>')
        # TODO: рефакторить получение имени и фамилии
        f.write('<first-name>' + ranobe_info['author'].split(' ')[0] + '</first-name>')
        f.write('<last-name>' + ranobe_info['author'].split(' ')[1] + '</last-name>')
        f.write('</author>')

        f.write('<annotation>')
        annotation = ''
        for line in ranobe_info['annotation'].split('\n'):
            annotation += '<p>{}</p>'.format(line)
        f.write(annotation)
        f.write('</annotation>')

        f.write('</title-info>')
        f.write('</description>')
        # f.write('<body>' + '<p>' + 'Hello мир!' + '</p>' + '</body>')
        f.write('</FictionBook>')