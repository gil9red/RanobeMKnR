__author__ = 'ipetrash'

# Добавление из относительного пути
import sys
sys.path.append('../pyfb2')


import fb2


if __name__ == '__main__':
    book = fb2.FB2()
    print(book.get_source())