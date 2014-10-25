__author__ = 'ipetrash'

"""Модуль для возвращения информации о томе ранобе."""

from urllib.parse import urljoin
from urllib.parse import urlparse
import os.path

from grab import Grab


def get_url2full_image_cover(g, url_ranobe):
    """Функция возвращает путь к картинке обложки тома."""

    # Относительная ссылка к обложки тома
    relative_url_cover = g.doc.select('//td[@id="cover"]/a').attr('href')

    # Соединение адреса к главной странице ранобе и относительной ссылки к обложке тома
    url_cover_volume = urljoin(url_ranobe, relative_url_cover)

    # Переход на страницу обложки
    g.go(url_cover_volume)
    relative_url_full_cover = g.doc.select('//div[@class="fullImageLink"]/a').attr('href')

    # Соединение адреса к главной странице ранобе и относительной
    # ссылки к полной картике обложке тома
    url_full_cover_volume = urljoin(url_ranobe, relative_url_full_cover)

    return url_full_cover_volume


def get_volume_base_page(url):
    """Функция возвратит базовую страницу url, например для
    http://ruranobe.ru/r/mknr/v12/ch1 вернется ch1,
    а для http://ruranobe.ru/r/mknr/v8/a?action=edit&redlink=1
    будет возвращено a."""

    path = urlparse(url).path
    base_url = os.path.basename(path)
    return base_url


# Список типов страниц тома
PAGE_TYPES_VOLUME = (
    'text',  # Содержание
    'i',     # Начальные иллюстрации
    'p1',    # Вступление
    'p2',    # Пролог
    'c',     # Страницы, которые начинаются с 'c' ('ch*', c*ch*)
    'e',     # Эпилог
    'ss',    # Дополнительная история
    'a',     # Послесловие
    'a2',    # Запоздавший шедевр
    'at',    # Послесловие команды перевода
)

# Тип страниц тома, которые не будут добавлены в файл инфо
BLACK_LIST_PAGE_TYPES = ('at', 'text')


def check_type_volume_pages(type_page):
    """Функция для проверки тип страниц тома. Если типа страниц
    type_page нет в списке, то функция вернет False, иначе True.
    """
    # Проверим тип страницы
    for t in PAGE_TYPES_VOLUME:
        # Если начало типа страницы совпадает с тем, что в списке, значит
        # такая страница есть
        if type_page.startswith(t):
            # Выходим из функции и возвращаем True
            return True

    # Страница не найдена в списке
    return False


def type_pages_is_chapter(type_pages):
    return type_pages.startswith("c")


def volume_info(url_volume, url_ranobe):
    """Функция возвращает словарь, содержащий информацию о томе ранобе."""

    g = Grab()
    g.setup(hammer_mode=True)

    # Переходим на страницу тома
    g.go(url_volume)

    if g.response.code != 200:
        print("Страница: {}, код возврата: {}".format(url_volume, g.response.code))
        return

    # Получение списка глав из оглавления
    contents = g.doc.select('//div[@id="index"]//a')
    # Если нет содержания -- пропускаем том
    if not contents:
        print("Нет содержания: {}".format(url_volume))
        return

    # Ссылка к картинке обложки тома
    url_cover_volume = get_url2full_image_cover(g.clone(), url_ranobe)

    # Получаем список строк с двумя столбцами, каждая строка содержит
    # некоторую информацию о томе: названия на нескольких языка, серия,
    # автор, иллюстратор и т.п.
    list_info = g.doc.select('//table[@id="release-info"]/tr/td[2]')
    # volume_ja_name = list_info[0].text()  # Название тома на японском
    # volume_en_name = list_info[1].text()  # Название тома на английском
    volume_name = list_info[2].text()
    series = list_info[3].text()
    author = list_info[4].text()
    illustrator = list_info[5].text()
    volume_isbn = list_info[6].text()
    # status = list_info[7].text()  # Статус (наверное, статус перевода)
    tr_team = list_info[8].text()
    translators = list_info[9].text().split(', ')

    # Список глав тома
    chapters = list()

    # Остальные страниц, которые не относятся к главам тома
    other_pages = dict()

    # Словарь содержит информацию о томе
    info = {
        "name": volume_name,
        "series": series,
        "author": author,
        "illustrator": illustrator,
        "ISBN": volume_isbn,
        "url_cover": url_cover_volume,
        "pages": {
            "chapters": chapters,
            "other": other_pages,
        },
        "translation": {
            "team": tr_team,  # команда перевода
            "translators": translators,  # переводчики
        },
    }

    for ch in contents:
        # Адрес к главе тома
        url_chapter = urljoin(url_ranobe, ch.attr("href"))

        # Проверка на существование страницы с главой
        grab_chapter = Grab()
        grab_chapter.setup(hammer_mode=True)
        grab_chapter.go(url_chapter)

        # Тип страницы тома может быть "Начальные иллюстрации", "Пролог", сами главы, и т.п.
        # Типы страниц описаны выше данной функции.
        volume_base_page = get_volume_base_page(url_chapter)

        # TODO: учитывать, что главы могут делать на части,
        # например: c6ch1, c6ch2, c6ch3, c6ch4

        # Проверим тип страницы: если страница не найдена:
        if not check_type_volume_pages(volume_base_page):
            print('!!! Неизвестный тип страниц тома: {}'.format(volume_base_page))

        # Фильтр типов страниц, которые не будут добавлены в файл инфо
        if volume_base_page in BLACK_LIST_PAGE_TYPES:
            continue

        # Тут мы проверяем наличие глав тома: если не удачно, выходим из функции, без возврата тома
        if grab_chapter.response.code != 200:
            print("Не найдена глава: {}".format(url_chapter))

            # Если типом является глава, выходим -- нам не нужен том, у которого будут отсутствовать
            # какие то главы, а вот все остальным ("Начальные иллюстрации", "Пролог", "Эпилог",
            # "Послесловие", и т.п.) можно пренебречь
            if type_pages_is_chapter(volume_base_page):
                return

            # Пропускаем добавление страницы в список
            continue

        # Разбиение списка глав соответственно с типами страниц:
        # главы -- отдельно, а все остальное тоже отдельно.

        href_text = url_chapter, ch.text()

        # Если типом страницы является глава:
        if type_pages_is_chapter(volume_base_page):
            # Добавление адреса главы к списку
            chapters.append(href_text)
        else:
            # Добавляем в словарь данную страницу, которая не относится к главам
            other_pages[volume_base_page] = href_text

    return info