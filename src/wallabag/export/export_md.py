# -*- coding: utf-8 -*-

from .export import Export
from markdownify import markdownify


class ExportMd(Export):

    def __init__(self, entry):
        Export.__init__(self, entry)

    def run(self):
        return self.__output(
                self.entry.title,
                markdownify(self.entry.content, heading_style="ATX"))

    def __output(self, title, article):
        return (f"# {title}\n"
                f"{article}")
