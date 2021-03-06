# TODO: 2.2
# __author__ = 'ipetrash'
#
#
# """"""
#
#
# from person import Person
# from person import PersonItem
#
#
# class PublisherItem(PersonItem):
# """"""
#
# # Описание
#     # Используется в двух местах документа для разных целей.
#     # Изначально содержится в <publish-info>, и содержит название издателя
#     # оригинальной (бумажной) книги (текстовую строку).
#     # С версии 2.2 может также содержаться в <document-info>, в этом случае
#     # содержит информацию о правообладателе документа (ФИО или псевдоним, а
#     # также присваиваемый библиотекой идентификатор). Как выразился Грибов,
#     # "Кому баппки отдавать, если таковые будут".
#     #
#     # Атрибуты
#     # Если содержится в <publish-info>, то
#     # xml:lang (опционально) - язык текста.
#     # Если содержится в <document-info>, то нет атрибутов.
#     #
#     # Подчиненные элементы
#     # Если содержится в <publish-info>, то нет подчиненных элементов, содержит текстовую строку ? собственно название издателя книги.
#     # Если содержится в <document-info>, то должен содержать элементы описанные в <author>.
#     #
#     # Подчинен
#     # Может содержаться в следующих элементах:
#     # <publish-info> (опционально);
#     # <document-info> (опционально).
#     #
#     # Пример использования
#     # <publish-info>
#     #   <book-name>Долгин А.Б. Экономика символического обмена</book-name>
#     #   <publisher>Инфра-М</publisher>
#     #   <city>Москва</city>
#     #   <year>2006</year>
#     #   <isbn>5-16-002911-7</isbn>
#     # </publish-info>
#
#     # TODO: доделать
#
#     def __init__(self):
#         super().__init__()
#
#         self.name_tag = "publisher"
#
#
# class Publisher(Person):
#     """"""
#
#     # TODO: доделать
#
#     def __init__(self):
#         super().__init__()
#
#     def append(self, publisher=None):
#         if publisher:
#             self._list.append(publisher)
#         else:
#             publisher = PublisherItem()
#             self._list.append(publisher)
#             return publisher
#
#     def get_source(self):
#         # Список правообладателей необязательный, поэтому обойдемся
#         # без выбрасывания исключения и просто выйдем, если список пуст
#         if not __self.list:
#             return ''
#
#         source = ''
#         for p in __self.list:
#             source += p.get_source()
#
#         return source