# -*- coding: utf-8 -*-


class ExportHtml():

    def __init__(self):
        pass

    def export(self, html):
        return html

    def output(self, title, article):
        return (f"<h1>{title}</h1>\n"
                f"{article}")
