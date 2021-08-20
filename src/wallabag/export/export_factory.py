# -*- coding: utf-8 -*-

from .export_cli import ExportCli
from .export_html import ExportHtml
from .export_md import ExportMd
from wallabag.format_type import ScreenType


class ExportFactory():

    def create(entry, params, type, width):
        if type == ScreenType.MARKDOWN:
            return ExportMd(entry)
        elif type == ScreenType.TERM:
            return ExportCli(entry, params, width)
        else:
            return ExportHtml(entry)
