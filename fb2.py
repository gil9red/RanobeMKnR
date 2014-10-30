__author__ = 'ipetrash'

"""Модуль для создания документов FictionBook версии 2.0 (fb2)."""


# <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0"
# xmlns:l="http://www.w3.org/1999/xlink">
# <description>
#     ...
#   </description>
#   <body>
#     ...
#   </body>
#   <body name="notes">
#     ...
#   </body>
#   <binary id="cover.jpg" content-type="image/jpeg">/9j/
#     4AAQSkZJRgABAgAAZABkAAD/
#     ...
#   </binary>
# </FictionBook>


class Description:
    pass
    # <title-info> - 1 (один, обязателен);
    # <document-info> - 1 (один, обязателен);
    # <publish-info> - 0..1 (один, опционально);
    # <custom-info> - 0..n (любое число, опционально);


class Body:
    pass
    # <image> - 0..1 (один, опционально) - задается изображение
    # для отображения в начале книги (или конкретного <body>);
    # <title> - 0..1 (один, опционально) - задается заглавие
    # для отображения в начале книги (или конкретного <body>);
    # <epigraph> - 0..n (любое число, опционально) - задаются эпиграфы к книге;
    # <section> - 1..n (любое число, один обязaтелен) - задаются
    # части (главы, прочие структурные единицы) книги;


class Binary:
    pass
    # Не содержит подчиненных элементов.
    # Должен содержать текст, представляющий собой двоичные данные,
    # кодированные методом base64


class FB2:
    def __init__(self):
        self.description = Description()  # Одно и только одно вхождение
        self.body = [Body()]  # Одно или более вхождений
        self.binary = list()  # Любое число вхождений

    def add_body(self):
        self.body.append(Body())

    def add_binary(self):
        self.binary.append(Binary())