__author__ = 'ipetrash'

from grab import Grab

if __name__ == '__main__':
    url = 'http://ruranobe.ru/r/mknr/v1'

    g = Grab()
    g.go(url)

    # Получение основного контекста, имеющий номер главы и
    content_text = g.doc.select('//div[@id="mw-content-text"]')
    print(content_text.html())
