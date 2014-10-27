__author__ = 'ipetrash'

from grab import Grab
from urllib.parse import urljoin

# Скрипт для получения содержания томом с учетом двух уровней вложенности:
# главы и подглавы

url = 'http://ruranobe.ru/r/mknr/v5'

g = Grab()
g.go(url)

# Получение списка глав из оглавления
content = g.doc.select('//div[@id="index"]/ol/li')

chapters = list()

for i, c in enumerate(content, 1):
    # Проверяем на подсписок
    if c.node.find('ol') is not None:
        # Вывод названия элемента
        print("{}. {}:\n".format(i, c.node.text.strip()), end='')

        sub_chapters = list()
        chapters.append((c.node.text.strip(), sub_chapters))

        # И вывод его подсписка
        for j, ch in enumerate(content.select('ol/li/a'), 1):
            url_ch = urljoin(url, ch.attr('href'))
            print("  {}. '{}': {}".format(j, ch.text(), url_ch))
            sub_chapters.append((ch.text(), url_ch))
    else:
        url_ch = urljoin(url, c.select('a').attr('href'))
        print("{}. '{}': {}".format(i, c.text(), url_ch))
        chapters.append((c.text(), url_ch))

print(chapters)

# g = Grab()
# g.go('http://ruranobe.ru/r/mknr/v1/ch1')
#
# # Получение основного контекста, имеющий номер главы и
# content_text = g.doc.select('//div[@id="mw-content-text"]')
#
# print(content_text.html())