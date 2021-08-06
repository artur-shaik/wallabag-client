# -*- coding: utf-8 -*-

from markdownify import markdownify


class ExportMd():

    def html2md(self, html):
        return markdownify(html)
