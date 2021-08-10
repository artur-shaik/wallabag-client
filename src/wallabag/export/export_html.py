# -*- coding: utf-8 -*-

from .export import Export


class ExportHtml(Export):

    def __init__(self, entry):
        Export.__init__(self, entry)

    def run(self):
        return self.__output(self.entry.title, self.entry.content)

    def __output(self, title, article):
        return (f"<h1>{title}</h1>\n"
                f"{article}")
