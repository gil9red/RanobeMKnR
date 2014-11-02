__author__ = 'ipetrash'


from compile_ranobe import prepare_and_create_grab


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
    url = 'http://ruranobe.ru/r/mknr/v1/ch1'
    g = prepare_and_create_grab(url)


    # # ◊ ◊ ◊ -- разделители частей главы
    # for c in g.doc.select('//*[@class="subtitle"]'):
    #     print(c.text())


    content = g.doc.select('//div[@id="mw-content-text"]/p')
    for i, p in enumerate(content, 1):
        print('{}. "{}"'.format(i, p.html()))
        print('"{}"'.format(p.text()))
        print()



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