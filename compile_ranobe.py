__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""

import os.path
# import sys
import json

import generate_info_ranobe

from xml.dom.minidom import parseString


def pretty_xml(xml, ind=' ' * 2):
    """Функция принимает строку xml и выводит xml с отступами."""

    return parseString(xml).toprettyxml(indent=ind)


# from lxml import etree
#
# def pretty_xml(xml_str):
# """Функция принимает строку xml и выводит xml с отступами."""
#
#     root = etree.fromstring(xml_str)
#     return etree.tostring(root, pretty_print=True)


from urllib.request import urlopen
import base64


def get_base64_url_image(url_image):
    """Функция возвращает base64 изображения по url."""

    image = urlopen(url_image)
    return base64.b64encode(image.read()).decode("utf-8")


from grab import Grab


def add_chapter_to_fb2(url_chapter):
    """Скачивает главу по ссылке, формирует секцию section fb2 и заполняет ее"""

    if not url_chapter:
        return ''

    url, name = url_chapter

    g = Grab()
    g.go(url)

    # # Получение основного контекста, имеющий номер главы и
    # content_text = g.doc.select('//div[@id="mw-content-text"]')

    # # Получение и объединение параграфов в единый текст
    # content = ''.join('<p>{}</p>'.format(r.text()) for r in content_text.select('p'))

    section = '<section>'
    section += '<title><p>{}</p></title>'.format(name)
    # section += content
    section += '</section>'
    return section


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


    # Первый том
    volume_info = ranobe_info['volumes'][0]

    # TODO: имя файла с томом ранобе нужно такое же как и название тома
    # Название файла тома ранобе
    # name_volume_fb2 = volume_info['name'].replace(':', '.') + '.fb2'
    name_volume_fb2 = 'ranobe.fb2'

    # Путь к файлу ранобе
    path_volume_fb2 = os.path.join(ranobe_dir, name_volume_fb2)

    text_fb2 = ('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" '
                'xmlns:l="http://www.w3.org/1999/xlink">')

    text_fb2 += '<description>'


    # TODO: добавить информацию о переводчиках

    # TODO: Добавить инфу о исходном языке (<src-lang>): японский

    text_fb2 += '<title-info>'

    # Имя тома
    name_volume = volume_info['name']

    # Добавление имени тома
    text_fb2 += '<book-title>' + name_volume + '</book-title>'

    # Добавление автора
    text_fb2 += '<author>'
    first_name, last_name = tuple(volume_info['author'].split(' '))
    text_fb2 += '<first-name>' + first_name + '</first-name>'
    text_fb2 += '<last-name>' + last_name + '</last-name>'
    text_fb2 += '</author>'

    # Добавление иллюстратора
    text_fb2 += '<author>'
    first_name, last_name = tuple(volume_info['illustrator'].split(' '))
    text_fb2 += '<first-name>' + first_name + '</first-name>'
    text_fb2 += '<last-name>' + last_name + '</last-name>'
    text_fb2 += '</author>'

    # Добавление аннотации
    text_fb2 += '<annotation>'
    annotation = ''
    for line in ranobe_info['annotation'].split('\n'):
        annotation += '<p>{}</p>'.format(line)
    text_fb2 += annotation
    text_fb2 += '</annotation>'

    # Добавлени серии и номера в серии
    text_fb2 += '<sequence name="{}" number="{}"/>'.format(volume_info['series'], volume_info['number'])

    # Добавление жанра(ов)
    text_fb2 += '<genre>{}</genre>'.format('sf_fantasy')

    # Язык тома
    text_fb2 += '<lang>{}</lang>'.format('ru')

    # Обложка тома
    text_fb2 += '<coverpage><image l:href="#cover.png"/></coverpage>'

    text_fb2 += '</title-info>'


    # Информация о создателе документа fb2
    text_fb2 += '<document-info>'

    # Автор документа, т.е. тот, кто его создал/сгенерировал/сконвертировал.
    text_fb2 += '<author>'
    text_fb2 += '<nickname>{}</nickname>'.format('gil9red')
    text_fb2 += '<home-page>{}</home-page>'.format('https://github.com/gil9red')
    text_fb2 += '</author>'

    # TODO: добавить
    # Откуда взят оригинальный документ, доступный в online:
    # text_fb2 += '<src-url>{}</src-url>'.format('')

    # TODO: добавить
    # Перечисление программ, которые использовались при подготовке документа.
    # text_fb2 += '<program-used>{}</program-used>'.format('')

    # TODO: добавить
    # Версия документа
    # text_fb2 += '<version>{}</version>'.format('1.0')


    text_fb2 += '</document-info>'


    # Информация о бумажном (или другом) издании, на основании которого создан FB2.x документ.
    text_fb2 += '<publish-info>'
    text_fb2 += '<isbn>{}</isbn>'.format(volume_info['ISBN'])
    text_fb2 += '</publish-info>'

    text_fb2 += '</description>'

    text_fb2 += '<body>'


    text_fb2 += '<title><p>{}</p></title>'.format(name_volume)


    # Порядок глав (с типами страниц) в томе:
    #  i   - Начальные иллюстрации
    #  p1  - Вступление
    #  p2  - Пролог
    #  ch  - Главы
    #  ss  - Дополнительная история
    #  e   - Эпилог
    #  a   - Послесловие
    #  a2  - Запоздавший шедевр

    text_fb2 += add_chapter_to_fb2(volume_info.get('i'))
    text_fb2 += add_chapter_to_fb2(volume_info.get('p1'))
    text_fb2 += add_chapter_to_fb2(volume_info.get('p2'))

    for url in volume_info.get('chapters'):
        text_fb2 += add_chapter_to_fb2(url)

    text_fb2 += add_chapter_to_fb2(volume_info.get('ss'))
    text_fb2 += add_chapter_to_fb2(volume_info.get('e'))
    text_fb2 += add_chapter_to_fb2(volume_info.get('a'))
    text_fb2 += add_chapter_to_fb2(volume_info.get('a2'))

    text_fb2 += '</body>'


    # Добавление обложки
    url_cover = volume_info['url_cover']
    # Определение суффикса/типа файла изображения
    # # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> png
    # suffix = os.path.splitext(url_cover)[1][1:]
    # text_fb2 += '<binary id="cover.{0}" content-type="image/{0}">'.format(suffix)

    text_fb2 += '<binary id="cover.png" content-type="image/png">'
    text_fb2 += get_base64_url_image(url_cover)
    text_fb2 += '</binary>'

    text_fb2 += '</FictionBook>'

    # Открытие и перезапись файла ранобе
    with open(path_volume_fb2, mode='w', encoding='utf8') as f:
        xml = '<?xml version="1.0" encoding="UTF-8"?>' + '\n'
        xml += text_fb2
        f.write(pretty_xml(xml))