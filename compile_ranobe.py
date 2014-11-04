__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""


def prepare_and_create_grab(url):
    import os
    from os.path import exists
    from os.path import join

    def get_cache_name(url):
        l = url.lstrip('http://').split('/')
        return l[-2], l[-1]

    data = None

    cache_name = get_cache_name(url)
    dir_name = cache_name[0]
    file_name = cache_name[1] + '.html'
    file_path = join(generate_info_ranobe.DIR_RANOBE, 'cache', dir_name, file_name)

    if not exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    if not exists(file_path):
        g = Grab()
        g.go(url)
        with open(file_path, mode='w', encoding='utf8') as f:
            text = g.response.body
            f.write(text)
            if not data:
                data = text

    if not data:
        with open(file_path, encoding='utf8') as f:
            data = f.read()

    return Grab(data)


import os.path
import json

import generate_info_ranobe


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

    name, url = url_chapter

    section = '<section>'
    section += '<title><p>{}</p></title>'.format(name)

    # Если список, тогда создаем вложенную секцию с подглавами
    if isinstance(url, list):
        for sub_ch in url:
            section += add_chapter_to_fb2(sub_ch)
    else:
        g = prepare_and_create_grab(url)

        binaries = ''

        content = g.doc.select('//div[@id="mw-content-text"]/*')
        for p in content:
            tag = p.node.tag
            if tag == 'p':
                # TODO: примечания
                section += '<p>{}</p>'.format(p.text())

            elif tag == 'div':
                image_href = p.select('./*/a[@class="image fancybox"]/@data-fancybox-href')
                if image_href.count():
                    href = image_href.text()

                    # Определение суффикса/типа файла изображения
                    # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> png
                    id_im = os.path.split(href)[1]
                    # TODO: проверять формат изображения (как я помню, может быть png или jpg)
                    suffix = os.path.splitext(href)[1][1:]
                    binaries += '<binary id="{}" content-type="image/{}">'.format(id_im, suffix)
                    binaries += get_base64_url_image(href)
                    binaries += '</binary>'

                    section += '<image l:href="#{}"/>'.format(id_im)

            elif tag == 'center' and p.attr('class') == 'subtitle':
                # Разделителем из оригинального текста является: ◊ ◊ ◊,
                # но, по-моему, три звездочки "* * *" лучше.
                # section += '<subtitle>{}</subtitle>'.format(p.text())

                section += '<subtitle>* * *</subtitle>'



    section += '</section>'
    return section, binaries


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


    text_fb2 = ('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" '
                'xmlns:l="http://www.w3.org/1999/xlink">')

    binaries = ''


    # Первый том
    volume_info = ranobe_info['volumes'][0]

    # TODO: имя файла с томом ранобе нужно такое же как и название тома
    # Название файла тома ранобе
    # name_volume_fb2 = volume_info['name'].replace(':', '.') + '.fb2'
    name_volume_fb2 = 'ranobe.fb2'

    # Путь к файлу ранобе
    path_volume_fb2 = os.path.join(ranobe_dir, name_volume_fb2)


    description = '<description>'

    # TODO: добавить информацию о переводчиках

    # title-info
    description += '<title-info>'

    # Имя тома
    name_volume = volume_info['name']

    # Добавление имени тома
    description += '<book-title>' + name_volume + '</book-title>'

    # Добавление автора
    description += '<author>'
    first_name, last_name = tuple(volume_info['author'].split(' '))
    description += '<first-name>' + first_name + '</first-name>'
    description += '<last-name>' + last_name + '</last-name>'
    description += '</author>'

    # Добавление иллюстратора
    description += '<author>'
    first_name, last_name = tuple(volume_info['illustrator'].split(' '))
    description += '<first-name>' + first_name + '</first-name>'
    description += '<last-name>' + last_name + '</last-name>'
    description += '</author>'

    # Добавление аннотации
    description += '<annotation>'
    annotation = ''
    for line in ranobe_info['annotation'].split('\n'):
        annotation += '<p>{}</p>'.format(line)
    description += annotation
    description += '</annotation>'

    # Добавлени серии и номера в серии
    description += '<sequence name="{}" number="{}"/>'.format(volume_info['series'], volume_info['number'])

    # Добавление жанра(ов)
    description += '<genre>{}</genre>'.format('sf_fantasy')

    # Язык тома
    description += '<lang>{}</lang>'.format('ru')

    # Исходный язык
    description += '<src-lang>{}</src-lang>'.format('jp')

    # Обложка тома
    description += '<coverpage><image l:href="#cover.png"/></coverpage>'

    description += '</title-info>'

    # document-info
    # Информация о создателе документа fb2
    description += '<document-info>'

    # Автор документа, т.е. тот, кто его создал/сгенерировал/сконвертировал.
    description += '<author>'
    description += '<nickname>{}</nickname>'.format('gil9red')
    description += '<home-page>{}</home-page>'.format('https://github.com/gil9red')
    description += '</author>'

    # TODO: добавить ссылка на сайт переводчиков ранобе, откуда, собственно, скрипт
    # и берет данные
    # Откуда взят оригинальный документ, доступный в online:
    # description += '<src-url>{}</src-url>'.format('')

    # TODO: добавить
    # Перечисление программ, которые использовались при подготовке документа.
    # description += '<program-used>{}</program-used>'.format('')

    # Версия документа
    description += '<version>{}</version>'.format('1.0')

    description += '</document-info>'


    # Информация о бумажном (или другом) издании, на основании которого создан FB2.x документ.
    description += '<publish-info>'
    description += '<isbn>{}</isbn>'.format(volume_info['ISBN'])
    description += '</publish-info>'

    description += '</description>'


    body = '<body>'
    body += '<title><p>{}</p></title>'.format(name_volume)

    # Порядок глав (с типами страниц) в томе:
    # i    - Начальные иллюстрации
    # p1   - Вступление
    # p2   - Пролог
    # c    - Глава (т.е. страницы, начинающиеся с 'c': 'ch*', c*ch*)
    # e    - Эпилог
    # ss   - Похоже на дополнительную инфу
    # a    - Послесловие
    # a2   - Запоздавший шедевр
    # at   - Послесловие команды перевода

    # Список глав тома
    chapters = volume_info.get("pages").get("chapters")

    # Словарь страниц тома, которые не относятся к главам: послесловие, пролог, и т.д.
    other_pages = volume_info.get("pages").get("other")

    # TODO: временно!
    body_section, binary_section = add_chapter_to_fb2(chapters[1])
    body += body_section
    binaries += binary_section


    # body += add_chapter_to_fb2(other_pages.get('i'))
    # body += add_chapter_to_fb2(other_pages.get('p1'))
    # body += add_chapter_to_fb2(other_pages.get('p2'))

    # # Перебор список глав:
    # for url_ch in chapters:
    #     body += add_chapter_to_fb2(url_ch)

    # body += add_chapter_to_fb2(other_pages.get('e'))
    # body += add_chapter_to_fb2(other_pages.get('ss'))
    # body += add_chapter_to_fb2(other_pages.get('a'))
    # body += add_chapter_to_fb2(other_pages.get('a2'))

    body += '</body>'


    # Добавление обложки
    url_cover = volume_info['url_cover']
    # Определение суффикса/типа файла изображения
    # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> png
    # TODO: проверять формат изображения (как я помню, может быть png или jpg)
    suffix = os.path.splitext(url_cover)[1][1:]
    binary = '<binary id="cover.{0}" content-type="image/{0}">'.format(suffix)
    # binary = '<binary id="cover.png" content-type="image/png">'
    binary += get_base64_url_image(url_cover)
    binary += '</binary>'

    binaries += binary


    # Добавим description часть документа fb2
    text_fb2 += description

    # Добавление body часть документа fb2
    text_fb2 += body

    # Добавление binary часть документа fb2
    text_fb2 += binaries

    text_fb2 += '</FictionBook>'


    # Открытие и перезапись файла ранобе
    with open(path_volume_fb2, mode='w', encoding='utf8') as f:
        xml = text_fb2

        from xml.dom.minidom import parseString
        xml = parseString(xml).toprettyxml(indent=' ')
        f.write(xml)