__author__ = 'ipetrash'

""""""


class Publisher:
    """"""

    # Описание
    # Используется в двух местах документа для разных целей.
    # Изначально содержится в <publish-info>, и содержит название издателя
    # оригинальной (бумажной) книги (текстовую строку).
    # С версии 2.2 может также содержаться в <document-info>, в этом случае
    # содержит информацию о правообладателе документа (ФИО или псевдоним, а
    # также присваиваемый библиотекой идентификатор). Как выразился Грибов,
    # "Кому баппки отдавать, если таковые будут".
    #
    # Атрибуты
    # Если содержится в <publish-info>, то
    # xml:lang (опционально) - язык текста.
    # Если содержится в <document-info>, то нет атрибутов.
    #
    # Подчиненные элементы
    # Если содержится в <publish-info>, то нет подчиненных элементов, содержит текстовую строку ? собственно название издателя книги.
    # Если содержится в <document-info>, то должен содержать элементы описанные в <author>.
    #
    # Подчинен
    # Может содержаться в следующих элементах:
    # <publish-info> (опционально);
    # <document-info> (опционально).
    #
    # Пример использования
    # <publish-info>
    # <book-name>Долгин А.Б. Экономика символического обмена</book-name>
    # <publisher>Инфра-М</publisher>
    #   <city>Москва</city>
    #   <year>2006</year>
    #   <isbn>5-16-002911-7</isbn>
    # </publish-info>

    # TODO: доделать

    def __init__(self):
        self.lang = None
        self.text = None

    def get_source(self):
        if not self.text:
            raise NameError('Не указано название издателя оригинальной книги.')

        source = '<publisher'
        if self.lang:
            source += ' xml:lang="{}"'.format(self.lang)
        source += '>'
        source += self.text
        source += '</publisher>'
        return source