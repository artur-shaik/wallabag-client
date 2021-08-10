# -*- coding: utf-8 -*-

from markdownify import markdownify


class ExportMd():

    def export(self, html):
        return markdownify(html, heading_style="ATX")

    def output(self, title, article):
        return (f"# {title}\n"
                f"{article}")
