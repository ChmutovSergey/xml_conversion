# -*- coding: utf-8 -*-
import json
from lxml import etree

from .dict2xml import HASH_MAP


class Element:
    """
    Обертка на XML-дереве. Преобразует XML-документ к виду JSON-объекта.
    """

    def __init__(self, element):
        """
        :param: element a normal etree.Element instance
        """
        self.element = element

    def to_dict(self):
        """
        Возвращает элемент дерева XML в ввиде питоновского словаря.
        Рекурсивно обходит все дочерние элементы.
        """
        # формирует структуру JSON без вложенных параметров {value}
        rval = dict()
        # взводим флаг, для того чтобы элементы списка исходного файла, поместить в такую же структуру
        attrib_type = True if self.element.attrib.get('type') == 'list' else False

        # конвертируем словарь <HASH_MAP>. Меняем местами key <-> value
        change_map = {val: key for key, val in HASH_MAP.items()}
        if self.element.text:
            # производим подмену типов данных (преобразуя строки в исходный тип данных)
            cls_type = change_map.get(self.element.attrib.get('type'))  # cls_type == <class 'type'>
            value = cls_type(self.element.text) if cls_type else None
        # если <self.element.text> пустой, то выбираем тип <value> в зависимости от флага <attrib_type>
        else:
            value = list() if attrib_type else dict()

        # проверяем тег на то, был ли этот ключ словаря числом
        if self.element.tag == 'numeric':
            cls_type = change_map.get(self.element.attrib.get('tag-name-type'))  # cls_type == <class 'self-type'>
            rval.update({cls_type(self.element.attrib['value']): value})
        else:
            rval.update({self.element.tag: value})

        for child in self.element:
            if attrib_type:
                # формируем словарь всех детей
                ch_child = Element(child).to_dict()
                # обновляем родителя
                rval[self.element.tag].append(ch_child[child.tag])
            else:
                rval[self.element.tag].update(Element(child).to_dict())
        return rval


class XmlDocument:
    """
    Обертка lxml предоставляет:
        - более чистый доступ к некоторым lxml.etree функциям
        - конвертация из XML в питоновский словарь
        - конвертация из XML в JSON
    """

    def __init__(self, xml='<empty/>', filename=None):
        """
        Есть два возможных способа инициализации XML-документа:
            - в виде строки;
            - в виде файла.

        Нет необходимости инициализировать Xml-документ во время создания экземпляра.
        Это можно сделать позже с помощью метода "set".
        Если вы решите инициализировать позже, Xml-документ будет инициализирован с помощью "<empty/>".

        :param xml: используется этот аргумент если необходимо распарсить строку.
        :param filename: используется этот аргумент если необходимо распарсить файл.
        """
        self.set(xml, filename)

    def set(self, xml=None, filename=None):
        """
        Этот метод используется если необходимо переопределить XML-документ.

        :param xml: используется этот аргумент если необходимо распарсить строку.
        :param filename: используется этот аргумент если необходимо распарсить файл.
        """
        if filename:
            self.tree = etree.parse(filename)
            self.root = self.tree.getroot()
        else:
            self.root = etree.fromstring(xml)
            self.tree = etree.ElementTree(self.root)

    def dump(self):
        etree.dump(self.root)

    def get_xml(self):
        """
        Возвращает документ, как строку
        """
        return etree.tostring(self.root)

    def xpath(self, xpath):
        """
        Возвращает элементы, соответствующие заданному xpath

        :param: xpath
        """
        return self.tree.xpath(xpath)

    def nodes(self):
        """
        Возвращает все узлы
        """
        return self.root.iter('*')

    def to_dict(self):
        """
        Конвертирует в питоновский словарь.
        """
        return Element(self.root).to_dict()

    def to_json(self, indent=None):
        """
        Конвертирует в JSON-объект
        """
        return json.dumps(self.to_dict(), indent=indent)
