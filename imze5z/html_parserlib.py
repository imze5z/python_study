# -*- coding: utf-8 -*-
from scrapy.selector import Selector


class XPathParser(object):
    def __init__(self, text):
        self.res = Selector(text=text)

    def xpath(self, text):
        return self.res.xpath(text)
