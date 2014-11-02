__author__ = 'ipetrash'

import os


def prepare_and_create_grab(url):
    def get_cache_name(url):
        l = url.lstrip('http://').split('/')
        return l[-2] + '_' + l[-1]

    data = None

    file_name = get_cache_name(url) + '.html'
    file_path = join(generate_info_ranobe.DIR_RANOBE, 'cache', file_name)

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


from grab import Grab
from os.path import exists
from os.path import join
import generate_info_ranobe


def volume_references(grab_doc):
    """Функция возвращает словарь, ключем будет id примечания,
    а значением -- примечание главы."""

    content = grab_doc.select('//ol[@class="references"]/li')
    references = dict()
    for ref in content:
        ref_id = ref.attr('id')  # cite_note-*
        # ref_link = ref.select('span[@class="mw-cite-backlink"]/a').attr('href').strip()  # cite_ref-1
        ref_text = ref.select('span[@class="reference-text"]').text().strip()
        references[ref_id] = ref_text

    return references


def volume_images(grab_doc):
    """Функция возвращает список картинок в главе."""

    content = grab_doc.select('//a[@class="image fancybox"]')
    images = list()
    for im in content:
        href = im.attr('data-fancybox-href')
        images.append(href)

    return images


if __name__ == '__main__':
    url = 'http://ruranobe.ru/r/mknr/v1/ch0'
    g = prepare_and_create_grab(url)


    for p in g.doc.select('//div[@id="mw-content-text"]/p'):
        print(p.html())
        # print(p.text())



    # # Список картинок в главе
    # images = volume_images(g.doc)
    #
    # if images:
    #     # Перебор списка картинок главы
    #     print('Картинки:')
    #     for i, im in enumerate(images, 1):
    #         print('{}. {}'.format(i, im))
    # else:
    #     print('Картинок в главе нет.')
    #
    # print()
    #
    #
    # # Словарь с примечаниями, которые находятся в конце главы
    # references = volume_references(g.doc)
    #
    # if references:
    #     # Поиск примечаний в тексте главы:
    #     print('Примечания:')
    #     reference_content = g.doc.select('//*[@class="reference"]/a/@href')
    #     for i, ref in enumerate(reference_content, 1):
    #         ref_id = ref.text().lstrip('#')
    #         ref_text = references[ref_id]
    #         print('{}. {}: {}'.format(i, ref_id, ref_text))
    # else:
    #     print('Примечаний нет.')