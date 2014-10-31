__author__ = 'ipetrash'

from grab import Grab

if __name__ == '__main__':
    # url = 'http://ruranobe.ru/r/mknr/v1/ch1'

    data = None
    with open('_ranobe_\ch1.html', encoding='utf8') as f:
        data = f.read()

    g = Grab(data)

    # Получение основного контекста, имеющий номер главы и
    # content_text = g.doc.select('//div[@id="mw-content-text"]')
    # print(content_text.html())

    print(g.doc.select('//ol[@class="references"]').count())
    print(g.doc.select('//ol[@class="references"]/li').count())