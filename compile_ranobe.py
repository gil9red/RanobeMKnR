__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""


def split_url_by_volume_and_chapter(url):
    l = url.lstrip('http://').split('/')
    return l[-2], l[-1]


def prepare_and_create_grab(url):
    import os
    from os.path import exists
    from os.path import join

    data = None
    cache_name = split_url_by_volume_and_chapter(url)
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
# from urllib.request import urlopen
# import base64

import generate_info_ranobe


# def get_base64_url_image(url_image):
#     """Функция возвращает base64 изображения по url."""
#
#     image = urlopen(url_image)
#     return base64.b64encode(image.read()).decode("utf-8")


from grab import Grab

import re


def volume_references(grab_doc, prefix_ref_note):
    """Функция возвращает словарь, ключем будет id примечания,
    а значением -- примечание главы."""

    content = grab_doc.select('//ol[@class="references"]/li')
    references = dict()
    for ref in content:
        ref_id = ref.attr('id')  # cite_note-*
        # Добавим префикс:
        ref_id = prefix_ref_note + ref_id
        ref_text = ref.select('span[@class="reference-text"]').text().strip()
        references[ref_id] = ref_text

    return references


def add_chapter_to_fb2(url_chapter, book_fb2):
    """Скачивает главу по ссылке, формирует секцию section fb2 и заполняет ее"""

    # if not url_chapter:
    #     return '', '', ''

    if not url_chapter or not book_fb2:
        return

    name, url = url_chapter

    # # Секция с примечаниями
    # note_section = ''
    #
    # # Секция с картинками
    # binaries = ''


    # NOTE: pyfb2
    section = book.body.doc.section.append()
    section.title.append_paragraph().text = name

    # section = '<section>'
    # section += '<title><p>{}</p></title>'.format(name)

    # Если список, тогда создаем вложенную секцию с подглавами
    if isinstance(url, list):
        for sub_ch in url:
            # NOTE: pyfb2
            add_chapter_to_fb2(sub_ch, book_fb2)
            # body, binary_section, notes = add_chapter_to_fb2(sub_ch)
            # section += body
            # binaries += binary_section
            # note_section += notes
    else:
        g = prepare_and_create_grab(url)

        # Для главы: http://ruranobe.ru/r/mknr/v1/ch1
        # вернется "v1", "ch1"
        vol_num, ch_num = split_url_by_volume_and_chapter(url)
        prefix_note_ref = vol_num + "_" + ch_num + "_"

        # Словарь с примечаниями, которые находятся в конце главы
        refs_ch = volume_references(g.doc, prefix_note_ref)
        if refs_ch:
            # TODO: рефакторинг
            for i, key_ref in enumerate(sorted(refs_ch.keys()), 1):
                # NOTE: pyfb2
                book.body.notes.append(key_ref, i, refs_ch.get(key_ref))

                # note_section += '<section id="{}">'.format(key_ref)
                # note_section += '<title><p>{}</p></title>'.format(i)
                # note_section += '<p>{}</p>'.format(refs_ch.get(key_ref))
                # note_section += '</section>'

        note_ref_pattern = re.compile(r"<sup.*?</sup>")

        content = g.doc.select('//div[@id="mw-content-text"]/*')
        for p in content:
            tag = p.node.tag
            # TODO: найден заголовок: <h2><span class="mw-headline"
            if tag == 'p':
                refs = p.select('sup[@class="reference"]/a')
                text_p = ''
                pos = 0
                if refs.count():
                    p_html = p.html()

                    # for i, ref in enumerate(refs, 1):
                    for ref in refs:
                        ref_id = ref.attr('href').lstrip('#')
                        ref_id = prefix_note_ref + ref_id

                        m = note_ref_pattern.search(p_html, pos)
                        if not m:
                            continue

                        pos = m.start()

                        # TODO: возможно стоит вести счет примечаний по всему тому
                        # ref_text = '[{}]'.format(i)
                        # fb2_note = '<a l:href="#{}" type="note">{}</a>'.format(ref_id, ref_text)
                        fb2_note = '<a l:href="#{}" type="note">{}</a>'.format(ref_id, ref.text())
                        p_html = p_html.replace(m.group(), fb2_note)

                    text_p = p_html

                else:
                    text_p = p.html()

                text_p = text_p.replace('\n', '')
                text_p = text_p.replace('<b>', '<strong>')
                text_p = text_p.replace('</b>', '</strong>')
                text_p = text_p.replace('<i>', '<emphasis>')
                text_p = text_p.replace('</i>', '</emphasis>')
                text_p = text_p.replace('<br>', '<empty-line/>')

                # Находим гиперссылки на адреса и убираем их
                for ext_href in p.select('a[@class="external text"]'):
                    text_p = text_p.replace(ext_href.html().replace('\n', ''), ext_href.text())

                # NOTE: pyfb2
                section.append_source_text().text = text_p
                # section += text_p

            elif tag == 'div':
                image_href = p.select('./*/a[@class="image fancybox"]/@data-fancybox-href')
                if image_href.count():
                    href = image_href.text()

                    image = book_fb2.append_image(url=href)
                    section.append_image(image)

                    # # Получение id изображения
                    # # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> MKnR_v01_a.png
                    # id_im = os.path.split(href)[1]
                    #
                    # # Определение суффикса/типа файла изображения
                    # # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> png
                    # # TODO: проверять формат изображения (как я помню, может быть png или jpg)
                    # suffix = os.path.splitext(href)[1][1:]
                    # binaries += '<binary id="{}" content-type="image/{}">'.format(id_im, suffix)
                    # binaries += get_base64_url_image(href)
                    # binaries += '</binary>'
                    #
                    # section += '<image l:href="#{}"/>'.format(id_im)

            elif tag == 'center' and p.attr('class') == 'subtitle':
                # Разделителем из оригинального текста является: ◊ ◊ ◊,
                # но, по-моему, три звездочки "* * *" лучше.
                # section += '<subtitle>{}</subtitle>'.format(p.text())


                # NOTE: pyfb2
                section.append_subtitle()
                # section += '<subtitle>* * *</subtitle>'

    # section += '</section>'
    #
    # return section, binaries, note_section


# http://www.fictionbook.org/index.php/Описание_формата_FB2_от_Sclex
# http://www.fictionbook.org/index.php/Элементы_стандарта_FictionBook

from datetime import date

if __name__ == '__main__':
    # # Добавление из относительного пути модуля pyfb2
    # import sys
    # sys.path.append('../pyfb2')
    #
    # from pyfb2 import fb2
    #
    # book = fb2.FB2()
    # print(book.get_source())

    from pyfb2 import fb2
    from pyfb2.fb2_genres import Genres

    # Путь к папке с генерированной информацией
    ranobe_dir = generate_info_ranobe.DIR_RANOBE

    # Путь к файлу с инфой об ранобе
    ranobe_info_path = generate_info_ranobe.RANOBE_INFO_PATH

    ranobe_info = None

    # Открываем файл в режиме чтения
    with open(ranobe_info_path, mode='r', encoding='utf8') as f:
        # Десериализация данных в объекты python'а
        ranobe_info = json.load(f)


    # NOTE: pyfb2
    # Создание документа fb2
    book = fb2.FB2()



    # text_fb2 = ('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" '
    #             'xmlns:l="http://www.w3.org/1999/xlink">')
    #
    # binaries = ''


    # Третий том
    volume_info = ranobe_info['volumes'][2]

    # TODO: имя файла с томом ранобе нужно такое же как и название тома
    # Название файла тома ранобе
    # name_volume_fb2 = volume_info['name'].replace(':', '.') + '.fb2'
    name_volume_fb2 = 'ranobe_v2_pyfb2.fb2'

    # Путь к файлу ранобе
    path_volume_fb2 = os.path.join(ranobe_dir, name_volume_fb2)


    # description = '<description>'
    #
    # # TODO: добавить информацию о переводчиках
    #
    # # title-info
    # description += '<title-info>'

    # Имя тома
    name_volume = volume_info['name']


    # NOTE: pyfb2
    # Добавление имени тома
    book.description.title_info.book_title.text = name_volume

    # # Добавление имени тома
    # description += '<book-title>' + name_volume + '</book-title>'


    # NOTE: pyfb2
    # Добавление автора
    author = book.description.title_info.author.append()
    first_name, last_name = tuple(volume_info['author'].split(' '))
    author.first_name.text = first_name
    author.last_name.text = last_name

    # # Добавление автора
    # description += '<author>'
    # first_name, last_name = tuple(volume_info['author'].split(' '))
    # description += '<first-name>' + first_name + '</first-name>'
    # description += '<last-name>' + last_name + '</last-name>'
    # description += '</author>'


    # NOTE: pyfb2
    # Добавление иллюстратора
    illustrator = book.description.title_info.author.append()
    first_name, last_name = tuple(volume_info['illustrator'].split(' '))
    author.first_name.text = first_name
    author.last_name.text = last_name

    # # Добавление иллюстратора
    # description += '<author>'
    # first_name, last_name = tuple(volume_info['illustrator'].split(' '))
    # description += '<first-name>' + first_name + '</first-name>'
    # description += '<last-name>' + last_name + '</last-name>'
    # description += '</author>'


    # NOTE: pyfb2
    # Добавление аннотации
    for row in ranobe_info['annotation'].split('\n'):
        book.description.title_info.annotation.append_paragraph().text = row

    # # Добавление аннотации
    # description += '<annotation>'
    # annotation = ''
    # for line in ranobe_info['annotation'].split('\n'):
    #     annotation += '<p>{}</p>'.format(line)
    # description += annotation
    # description += '</annotation>'


    # NOTE: pyfb2
    # Добавлени серии и номера в серии
    book.description.title_info.sequence.append(volume_info['series'], volume_info['number'])

    # # Добавлени серии и номера в серии
    # description += '<sequence name="{}" number="{}"/>'.format(volume_info['series'], volume_info['number'])


    # NOTE: pyfb2
    # Добавление жанра(ов)
    book.description.title_info.genre.append(Genres.sf_fantasy.value)

    # # Добавление жанра(ов)
    # description += '<genre>{}</genre>'.format('sf_fantasy')


    # NOTE: pyfb2
    # Язык тома
    book.description.title_info.lang.value = 'ru'

    # # Язык тома
    # description += '<lang>{}</lang>'.format('ru')


    # NOTE: pyfb2
    # Исходный язык
    book.description.title_info.src_lang.value = 'jp'

    # # Исходный язык
    # description += '<src-lang>{}</src-lang>'.format('jp')


    # NOTE: pyfb2
    # Обложка тома
    cover_image = book.append_image(url=volume_info['url_cover'])
    book.description.title_info.coverpage.append(cover_image)

    # # Обложка тома
    # description += '<coverpage><image l:href="#cover.png"/></coverpage>'


    # description += '</title-info>'


    # # document-info
    # # Информация о создателе документа fb2
    # description += '<document-info>'


    # NOTE: pyfb2
    document_info = book.description.document_info


    # NOTE: pyfb2
    # Автор документа, т.е. тот, кто его создал/сгенерировал/сконвертировал.
    doc_author = document_info.author.append()
    doc_author.nickname.text = 'gil9red'
    doc_author.home_page.append('https://github.com/gil9red')

    # # Автор документа, т.е. тот, кто его создал/сгенерировал/сконвертировал.
    # description += '<author>'
    # description += '<nickname>{}</nickname>'.format('gil9red')
    # description += '<home-page>{}</home-page>'.format('https://github.com/gil9red')
    # description += '</author>'


    # NOTE: pyfb2
    document_info.date.set_from_date(date.today())


    isbn = volume_info['ISBN']

    # NOTE: pyfb2
    document_info.id.value = isbn


    # TODO: добавить ссылки на сайт переводчиков ранобе, откуда, собственно, скрипт
    # и берет данные
    # Откуда взят оригинальный документ, доступный в online:
    # description += '<src-url>{}</src-url>'.format('')


    # TODO: добавить
    # Перечисление программ, которые использовались при подготовке документа.
    # description += '<program-used>{}</program-used>'.format('')


    # NOTE: pyfb2
    # Версия документа
    book.description.document_info.version.value = '1.0'

    # # Версия документа
    # description += '<version>{}</version>'.format('1.0')


    # description += '</document-info>'


    # NOTE: pyfb2
    # Информация о бумажном (или другом) издании, на основании которого создан FB2.x документ.
    book.description.publish_info.isbn.text = isbn

    # # Информация о бумажном (или другом) издании, на основании которого создан FB2.x документ.
    # description += '<publish-info>'
    # description += '<isbn>{}</isbn>'.format(volume_info['ISBN'])
    # description += '</publish-info>'


    # description += '</description>'


    # NOTE: pyfb2
    # заглавие для отображения в начале книги
    book.body.doc.title.append_paragraph().text = name_volume

    # body = '<body>'
    # body += '<title><p>{}</p></title>'.format(name_volume)


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


    # NOTE: pyfb2
    book.body.notes.title.append_paragraph().text = 'Примечания'

    # body_notes = '<body name="notes">'
    # body_notes += '<title><p>Примечания</p></title>'


    # # TODO: временно!
    # body_section, binary_section, note_section = add_chapter_to_fb2(chapters[1])
    # body += body_section
    # binaries += binary_section


    # # TODO: Убраны начальные иллюстрации
    # add_chapter_to_fb2(other_pages.get('i'), book_fb2=book)
    # # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('i'))
    # # body += body_section
    # # body_notes += note_section
    # # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('p1'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('p1'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('p2'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('p2'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section

    # Перебор списка глав:
    for url_ch in chapters:
        # NOTE: pyfb2
        add_chapter_to_fb2(url_ch, book_fb2=book)
        # body_section, binary_section, note_section = add_chapter_to_fb2(url_ch)
        # body += body_section
        # body_notes += note_section
        # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('e'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('e'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('ss'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('ss'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('a'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('a'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section

    # NOTE: pyfb2
    add_chapter_to_fb2(other_pages.get('a2'), book_fb2=book)
    # body_section, binary_section, note_section = add_chapter_to_fb2(other_pages.get('a2'))
    # body += body_section
    # body_notes += note_section
    # binaries += binary_section


    # body_notes += '</body>'
    #
    # body += '</body>'


    # # Добавление обложки
    # url_cover = volume_info['url_cover']
    # # Определение суффикса/типа файла изображения
    # # http://ruranobe.ru/w/images/3/3b/MKnR_v01_a.png -> png
    # # TODO: проверять формат изображения (как я помню, может быть png или jpg)
    # suffix = os.path.splitext(url_cover)[1][1:]
    # binary = '<binary id="cover.{0}" content-type="image/{0}">'.format(suffix)
    # # binary = '<binary id="cover.png" content-type="image/png">'
    # binary += get_base64_url_image(url_cover)
    # binary += '</binary>'

    # binaries += binary


    # # Добавим description часть документа fb2
    # text_fb2 += description
    #
    # # Добавление body часть документа fb2
    # text_fb2 += body
    #
    # # Добавление body с примечаниями
    # text_fb2 += body_notes
    #
    # # Добавление binary часть документа fb2
    # text_fb2 += binaries
    #
    # text_fb2 += '</FictionBook>'


    # # Открытие и перезапись файла ранобе
    # with open(path_volume_fb2, mode='w', encoding='utf8') as f:
    #     xml = text_fb2
    #
    #     from xml.dom.minidom import parseString
    #
    #     xml = parseString(xml).toprettyxml(indent=' ')
    #     f.write(xml)


    book.save(path_volume_fb2)