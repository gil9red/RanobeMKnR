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
    'i',  # Начальные иллюстрации
    'p1',  # Вступление
    'p2',  # Пролог
    'c',  # Страницы, которые начинаются с 'c' ('ch*', c*ch*)
    'e',  # Эпилог
    'ss',  # Дополнительная история
    'a',  # Послесловие
    'a2',  # Запоздавший шедевр
    'at',  # Послесловие команды перевода
)

# Тип страниц тома, которые не будут добавлены в файл инфо
BLACK_LIST_PAGE_TYPES = ('at', )


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


def get_volume_pages(grab_url_volume):
    """Функция возвращает содержание тома с учетом двух уровней
    вложенности: главы и подглавы"""

    # Адрес тома
    url_volume = grab_url_volume.response.url

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
                url_ch = urljoin(url_volume, ch.attr('href'))
                sub_chapters.append((ch.text(), url_ch))
        else:
            url_ch = urljoin(url_volume, c.select('a').attr('href'))
            chapters.append((c.text(), url_ch))

    return chapters


def check_volume_page(url_page):
    # Проверка на существование страницы с главой
    grab_chapter = Grab()
    grab_chapter.setup(hammer_mode=True)
    grab_chapter.go(url_page)

    # Тип страницы тома может быть "Начальные иллюстрации", "Пролог", сами главы, и т.п.
    # Типы страниц описаны выше данной функции.
    volume_base_page = get_volume_base_page(url_page)

    # Проверим тип страницы: если страница не найдена:
    if not check_type_volume_pages(volume_base_page):
        print('!!! Неизвестный тип страниц тома: {}'.format(volume_base_page))

    # Фильтр типов страниц, которые не будут добавлены в файл инфо
    if volume_base_page in BLACK_LIST_PAGE_TYPES:
        return None

    # Тут мы проверяем наличие глав тома: если не удачно, выходим из функции, без возврата тома
    if grab_chapter.response.code != 200:
        print("Не найдена глава: {}".format(url_page))

        # Если типом является глава, выходим -- нам не нужен том, у которого будут отсутствовать
        # какие то главы, а вот все остальным ("Начальные иллюстрации", "Пролог", "Эпилог",
        # "Послесловие", и т.п.) можно пренебречь
        if type_pages_is_chapter(volume_base_page):
            return False

        # Пропускаем добавление страницы в список
        return None

    return True


def volume_info(url_volume, url_ranobe):
    """Функция возвращает словарь, содержащий информацию о томе ранобе."""

    g = Grab()
    g.setup(hammer_mode=True)

    # Переходим на страницу тома
    g.go(url_volume)

    if g.response.code != 200:
        print("Страница: {}, код возврата: {}".format(url_volume, g.response.code))
        return

    # Ссылка к картинке обложки тома
    url_cover_volume = get_url2full_image_cover(g.clone(), url_ranobe)

    # Получаем список строк с двумя столбцами, каждая строка содержит
    # некоторую информацию о томе: названия на нескольких языка, серия,
    # автор, иллюстратор и т.п.
    list_info = g.doc.select('//table[@id="release-info"]/tr/td[2]')
    # volume_ja_name = None  # Название тома на японском
    # volume_en_name = None  # Название тома на английском
    volume_name = None
    series = None
    author = None
    illustrator = None
    volume_isbn = None
    # status = None  # Статус (наверное, статус перевода)
    tr_team = None
    translators = None

    try:
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
    except IndexError:
        print("Не хватает полей с информацией о томе: {}".format(url_volume))

    # Получение списка глав тома из оглавления
    volume_pages = get_volume_pages(g)
    # Если нет содержания -- пропускаем том
    if not volume_pages:
        print("Нет содержания: {}".format(url_volume))
        return

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

    # Переберем все страницы тома
    for page in volume_pages:
        # Адрес к главе тома
        name_ch, url_ch = page

        if not isinstance(url_ch, list):
            check = check_volume_page(url_ch)
            if check is False:
                return
            elif check is None:
                continue
        else:
            # Проверяем подглавы:
            for sub_ch in url_ch:
                sub_name, sub_url = sub_ch
                check = check_volume_page(sub_url)
                if check is False:
                    return
                elif check is None:
                    continue

        # Разбиение списка глав соответственно с типами страниц:
        # главы -- отдельно, а все остальное тоже отдельно.

        # Если адресом является список подглав
        if isinstance(url_ch, list):
            # Добавление списка подглав
            chapters.append(page)
        else:
            # Тип страницы тома может быть "Начальные иллюстрации", "Пролог", сами главы, и т.п.
            # Типы страниц описаны выше данной функции.
            volume_base_page = get_volume_base_page(url_ch)

            # Если типом страницы является глава:
            if type_pages_is_chapter(volume_base_page):
                # Добавление адреса главы к списку
                chapters.append(page)
            else:
                # Добавляем в словарь данную страницу, которая не относится к главам
                other_pages[volume_base_page] = page

    return info