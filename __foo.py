__author__ = 'ipetrash'


from grab import Grab
from os.path import exists
from os.path import join
import generate_info_ranobe


def volume_references(grab_volume):
    """Функция возвращает список примечаний главы."""

    content = grab_volume.doc.select('//ol[@class="references"]/li')
    references = list()
    for ref in content:
        ref_id = ref.attr('id')
        ref_link = ref.select('span[@class="mw-cite-backlink"]/a').attr('href').strip()
        ref_text = ref.select('span[@class="reference-text"]').text().strip()
        references.append((ref_link, ref_id, ref_text))

    return references


if __name__ == '__main__':
    data = None

    file_path = join(generate_info_ranobe.DIR_RANOBE, 'ch1.html')
    if not exists(file_path):
        url = 'http://ruranobe.ru/r/mknr/v1/ch1'
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


    g = Grab(data)

    # Получение основного контекста, имеющий номер главы и
    # content_text = g.doc.select('//div[@id="mw-content-text"]')
    # print(content_text.html())


    for i, ref in enumerate(volume_references(g), 1):
        print("{}. {} {} {}".format(i, ref[0], ref[1], ref[2]))

    print()

    # Поиск примечаний в тексте главы:
    content = g.doc.select('//*[@class="reference"]')
    for i, ref in enumerate(content, 1):
        href = ref.select("a/@href").text()
        print('{}. {} {}'.format(i, ref.attr('id'), href))
        # print('{}. {}'.format(i, href.text()))