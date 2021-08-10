# -*- coding: utf-8 -*-

from wallabag.format_type import ScreenType
from .export_cli import ExportCli
from .export_html import ExportHtml
from .export_md import ExportMd


class Export():

    def __init__(self):
        pass

    def export(self, html):
        pass

    def output(self, title, article):
        pass

    def get(params, width, annotations):
        if params.type == ScreenType.MARKDOWN:
            return ExportMd()
        elif params.type == ScreenType.TERM:
            return ExportCli(params, width, annotations)
        else:
            return ExportHtml()
