import os
import json
import re
import datetime
import gc

from grab import Grab

import generate_info_ranobe
from pyfb2 import fb2
from pyfb2.fb2_genres import Genres


__author__ = 'ipetrash'

"""Скрипт, используя данные скриптов get_ranobe_info и download_ranobe,
генерирует файл в формате fb2."""


def split_url_by_volume_and_chapter(url):
    l = url.lstrip('http://').split('/')
    return l[-2], l[-1]


def prepare_and_create_grab(url):

    cache_name = split_url_by_volume_and_chapter(url)
    dir_name = cache_name[0]
    file_name = cache_name[1] + '.html'
    file_path = os.path.join(generate_info_ranobe.DIR_RANOBE, 'cache', dir_name, file_name)
    data = None

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    if not os.path.exists(file_path):
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


def add_chapter_to_fb2(url_chapter, book_fb2, parent_section=None):
    """Скачивает главу по ссылке, формирует секцию section fb2 и заполняет ее."""

    if not url_chapter or not book_fb2:
        return

    name, url = url_chapter

    section = None

    if not parent_section:
        section = book.body.doc.section.append()
    else:
        section = parent_section.append_sub_section()

    section.title.append_paragraph().text = name

    # Если список, тогда создаем вложенную секцию с подглавами
    if isinstance(url, list):
        for sub_ch in url:
            add_chapter_to_fb2(sub_ch, book_fb2, parent_section=section)
    else:
        g = prepare_and_create_grab(url)

        # Для главы: http://ruranobe.ru/r/mknr/v1/ch1
        # вернется "v1", "ch1"
        vol_num, ch_num = split_url_by_volume_and_chapter(url)
        prefix_note_ref = vol_num + "_" + ch_num + "_"

        # Словарь с примечаниями, которые находятся в конце главы
        refs_ch = volume_references(g.doc, prefix_note_ref)
        if refs_ch:
            all_refs = sorted(refs_ch.keys())
            notes = book.body.notes
            for i, key_ref in enumerate(all_refs, 1):
                text = refs_ch.get(key_ref)
                notes.append(key_ref, str(i), text)

        note_ref_pattern = re.compile(r"<sup.*?</sup>")

        content = g.doc.select('//div[@id="mw-content-text"]/*')
        for p in content:
            tag = p.node.tag

            # TODO: найден в начальных иллюстрациях заголовок:
            # <h2><span class="mw-headline"

            if tag == 'p':
                refs = p.select('sup[@class="reference"]/a')
                text_p = ''
                pos = 0
                if refs.count():
                    p_html = p.html()

                    for ref in refs:
                        ref_id = ref.attr('href').lstrip('#')
                        ref_id = prefix_note_ref + ref_id

                        m = note_ref_pattern.search(p_html, pos)
                        if not m:
                            continue

                        pos = m.start()

                        # TODO: возможно стоит вести счет примечаний по всему тому
                        fb2_note = '<a xlink:href="#{}" type="note">{}</a>'.format(ref_id, ref.text())
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

                section.append_source_text().text = text_p

            elif tag == 'div':
                image_href = p.select('./*/a[@class="image fancybox"]/@data-fancybox-href')
                if image_href.count():
                    href = image_href.text()

                    image = book_fb2.append_image(url=href)
                    section.append_image(image)

            elif tag == 'center' and p.attr('class') == 'subtitle':
                section.append_subtitle()


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

    # Перебор томов ранобе:
    for volume_info in ranobe_info['volumes']:
        # Создание документа fb2
        book = fb2.FB2()

        # Название файла тома ранобе
        filename_volume_fb2 = volume_info['name'].replace(':', '.') + '.fb2'

        # Третий том
        # volume_info = ranobe_info['volumes'][2]

        # TODO: имя файла с томом ранобе нужно такое же как и название тома
        # Название файла тома ранобе
        # name_volume_fb2 = volume_info['name'].replace(':', '.') + '.fb2'
        # name_volume_fb2 = 'ranobe_v2_pyfb2.fb2'

        # Путь к файлу ранобе
        path_volume_fb2 = os.path.join(ranobe_dir, 'mknr', filename_volume_fb2)

        # Путь к папке, в которых будут сохранены fb2 документы ранобе
        dir_volume_fb2 = os.path.dirname(path_volume_fb2)
        if not os.path.exists(dir_volume_fb2):
            os.makedirs(dir_volume_fb2)

        # Описание информации о произведении
        title_info = book.description.title_info

        # Добавление информации о переводчиках:
        translation = volume_info.get('translation')
        if translation:
            translators = translation.get('translators')
            if translators:
                for tr_name in translators:
                    translator = title_info.translator.append()
                    translator.nickname.text = tr_name

        # Имя тома
        name_volume = volume_info['name']

        # Международный стандартный книжный номер (англ. International Standard Book Number,
        # сокращённо — англ. ISBN) — уникальный номер книжного издания, необходимый для
        # распространения книги в торговых сетях и автоматизации работы с изданием.
        isbn = volume_info['ISBN']

        # Метаинформация о книге
        description = book.description

        # Добавление имени тома
        book_title = description.title_info.book_title
        book_title.text = name_volume

        # Добавление автора
        author = description.title_info.author.append()
        first_name, last_name = tuple(volume_info['author'].split(' '))
        author.first_name.text = first_name
        author.last_name.text = last_name

        # Добавление иллюстратора
        illustrator = description.title_info.author.append()
        first_name, last_name = tuple(volume_info['illustrator'].split(' '))
        illustrator.first_name.text = first_name
        illustrator.last_name.text = last_name

        # Добавление аннотации
        annotation = description.title_info.annotation
        for row in ranobe_info['annotation'].split('\n'):
            annotation.append_paragraph().text = row

        # Добавлени серии и номера в серии
        sequence = description.title_info.sequence
        sequence.append(volume_info['series'], volume_info['number'])

        # Добавление жанра(ов)
        genre = description.title_info.genre
        genre.append(Genres.sf_fantasy.value)

        # Язык тома
        lang = description.title_info.lang
        lang.value = 'ru'

        # Исходный язык
        src_lang = description.title_info.src_lang
        src_lang.value = 'jp'

        # Обложка тома
        cover_image = book.append_image(url=volume_info['url_cover'])
        coverpage = description.title_info.coverpage
        coverpage.append(cover_image)

        # Описание информации о конкретном FB2.x документе
        document_info = description.document_info

        # Автор документа, т.е. тот, кто его создал/сгенерировал/сконвертировал.
        doc_author = document_info.author.append()
        doc_author.nickname.text = 'gil9red'
        doc_author.home_page.append('https://github.com/gil9red')

        # Дата создания документа
        date = document_info.date
        date.set_from_date(datetime.date.today())

        # Уникальный идентификатор документа FB2
        # Мне кажется ISBN годный уникальный идентификатор
        document_info.id.value = isbn

        # Откуда взят оригинальный документ, доступный в online:
        src_url = document_info.src_url
        src_url.append('http://ruranobe.ru/r/mknr')  # Сайт, с которого скрипт вытаскивает ранобе

        # Перечисление программ, которые использовались при подготовке документа.
        program_used = document_info.program_used
        program_used.append('RanobeMKnR')

        # Версия документа
        document_info.version.value = '1.0'

        # Информация о бумажном (или другом) издании, на основании которого создан FB2.x документ.
        publish_info = description.publish_info
        publish_info.isbn.text = isbn

        # Заглавие для отображения в начале книги
        title = book.body.doc.title
        title.append_paragraph().text = name_volume

        # Список глав тома
        chapters = volume_info.get("pages").get("chapters")

        # Словарь страниц тома, которые не относятся к главам: послесловие, пролог, и т.д.
        other_pages = volume_info.get("pages").get("other")

        # Примечания:
        notes_title = book.body.notes.title
        title.append_paragraph().text = 'Примечания'

        # # TODO: Убраны начальные иллюстрации
        # add_chapter_to_fb2(other_pages.get('i'), book)  # Начальные иллюстрации

        add_chapter_to_fb2(other_pages.get('p1'), book)  # Вступление
        add_chapter_to_fb2(other_pages.get('p2'), book)  # Пролог

        # Перебор списка глав:
        for url_ch in chapters:
            add_chapter_to_fb2(url_ch, book)

        add_chapter_to_fb2(other_pages.get('e'), book)  # Эпилог
        add_chapter_to_fb2(other_pages.get('ss'), book)  # Похоже на дополнительную инфу
        add_chapter_to_fb2(other_pages.get('a'), book)  # Послесловие
        add_chapter_to_fb2(other_pages.get('a2'), book)  # Запоздавший шедевр

        book.save(path_volume_fb2)

        # Подсчитываем размер файла документа fb2
        size = os.path.getsize(path_volume_fb2)  # bytes
        size /= 1024  # kb
        size /= 1024  # mb
        size = round(size, 2)
        print('Закончена генерация "{}", размер {} MB.'.format(name_volume, size))

        # Вызываем сборщик мусора
        gc.collect()