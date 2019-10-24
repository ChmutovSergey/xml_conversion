# -*- coding: utf-8 -*-
from xml.dom.minidom import Document

from ..core import PY_2


HASH_MAP = {
        bool: "bool",
        int: "int",
        str: "str",
        float: "float",
        tuple: "tuple",
        bytes: "bytes",
    }

if PY_2:  # скрипт запущен в python2
    HASH_MAP.update({unicode: "unicode"})


class DictToXML(object):
    """
    Конвертирует JSON-объект в XML-документ
    """

    def __init__(self, structure, h_book):
        """
        Инициализация атрибутов
        :param structure: {dict} содержит тело сообщения
        :param h_book: {dict} содержит справочник
        """
        self.doc = Document()
        if len(structure) == 1:
            try:
                raw_name = structure.keys()[0]
            except TypeError:
                raw_name = list(structure)[0]

            root_name = str(raw_name)
            self.root = self.doc.createElement(root_name)

            self.h_book = h_book
            self.doc.appendChild(self.root)
            self.build(self.root, structure[root_name])

    def build(self, father, structure):
        """
        Рекурсивно проходит по JSON-объекту, генерируя структуру XML-дерева
        :param father: объект XML-дерева, родительского узла
        :param structure: JSON-объект
        :return: None
        """
        if isinstance(structure, dict):
            for key in structure:
                k_type = self.get_structure_type(key)
                # если тег был числом, то добавляем дополнительные атрибуты:
                # <value> - с ключом словаря
                # <self-type> с типом данных ключа словаря
                if k_type in ('int', 'float'):
                    tag = self.doc.createElement("numeric")
                    tag.setAttribute("value", str(key))
                else:
                    key = key.encode('utf-8')
                    tag = self.doc.createElement(key)

                c_key = self.h_book.get(tag.tagName)
                if c_key:
                    tag.setAttribute("classificator", c_key)

                tag.setAttribute("type", "dict")  # атрибут с типом вложенной структуры
                tag.setAttribute("tag-name-type", k_type)  # атрибут с типом ключа словаря

                father.appendChild(tag)
                self.build(tag, structure[key])
        elif isinstance(structure, list):
            grand_father = father.parentNode
            tag_name = father.tagName

            grand_father.removeChild(father)
            tag = self.doc.createElement(tag_name)
            # цикл по вложенным тегам в списку
            for key, l in enumerate(structure):
                # создаем вложенный тег <element>, который является элементом питоновского списка
                l_child = self.doc.createElement('element-list')
                l_child.setAttribute("number", str(key))  # добавляем ему атрибут <number> с номером цикла
                self.build(l_child, l)
                # создаем родительский тег значением которого, является питоновский список
                tag.appendChild(l_child)
                tag.setAttribute("type", "list")  # добавляем ему атрибут <type> и указываем, что это был список
                tag.setAttribute("tag-name-type", self.get_structure_type(tag_name))  # атррибут с типом ключа словаря
                grand_father.appendChild(tag)
        else:
            try:
                data = str(structure)
            except UnicodeEncodeError:
                data = structure.encode('utf-8')

            tag = self.doc.createTextNode(data)
            father.setAttribute("type", self.get_structure_type(structure))  # атрибут с типом вложенной структуры
            father.setAttribute("tag-name-type", self.get_structure_type(data))  # атррибут с типом ключа словаря
            father.appendChild(tag)

    def display(self):
        """
        Выводит XML-документ на экран
        :return: None
        """
        print(self.doc.toprettyxml(indent="  "))

    def get_xml(self):
        """
        Возвращает сформированный XML-документ
        :return: None
        """
        return self.doc.toxml()

    @staticmethod
    def get_structure_type(structure):
        """
        Возвращает строковое имя типа структуры

        :param structure: object
        :return: string
        """
        try:
            h_type = HASH_MAP[type(structure)]
        except KeyError:
            h_type = "NoneType"

        return h_type
