__author__ = 'ipetrash'

from grab import Grab
from urllib.parse import urljoin


def get_chapters(grab_url_volume):
    """Функция возвращает содержание тома с учетом двух уровней
    вложенности: главы и подглавы"""

    # Получение списка глав из оглавления
    content = grab_url_volume.doc.select('//div[@id="index"]/ol/li')

    chapters = list()

    for c in content:
        # Проверяем на подсписок
        if c.node.find('ol') is not None:
            sub_chapters = list()
            chapters.append((c.node.text.strip(), sub_chapters))

            # Подсписок:
            for ch in content.select('ol/li/a'):
                url_ch = urljoin(url, ch.attr('href'))
                sub_chapters.append((ch.text(), url_ch))
        else:
            url_ch = urljoin(url, c.select('a').attr('href'))
            chapters.append((c.text(), url_ch))

    return chapters


if __name__ == '__main__':
    url = 'http://ruranobe.ru/r/mknr/v5'

    g = Grab()
    g.go(url)

    chapters = get_chapters(g)

    for ch in chapters:
        name, url = ch
        if not isinstance(url, list):
            print("'{}': {}".format(name, url))
        else:
            print("'{}':".format(name))
            for sub_ch in url:
                sub_name, sub_url = sub_ch
                print("    '{}': {}".format(sub_name, sub_url))


# g = Grab()
# g.go('http://ruranobe.ru/r/mknr/v1/ch1')
#
# # Получение основного контекста, имеющий номер главы и
# content_text = g.doc.select('//div[@id="mw-content-text"]')
#
# print(content_text.html())