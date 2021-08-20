# -*- coding: utf-8 -*-

import os
import textwrap
from enum import Enum, auto

from wallabag.api.get_entry import GetEntry
from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.entry import Entry
from wallabag.export.export_factory import ExportFactory
from wallabag.format_type import ScreenType


class Alignment(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()

    def list():
        return [c.name for c in Alignment]

    def get(name):
        for align in Alignment:
            if align.name == name.upper():
                return align
        return Alignment.CENTER


class ShowCommandParams(Params):
    width = '80%'
    align = Alignment.CENTER

    def __init__(self, entry_id, type=ScreenType.TERM, colors=True,
                 raw=False, image_links=False):
        self.entry_id = entry_id
        self.type = type
        self.colors = colors
        self.raw = raw
        self.image_links = image_links


class ShowCommand(Command):

    FAILWIDTH = 100

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        self.__calculate_alignment()

        api = GetEntry(self.config, self.params.entry_id)
        output = ExportFactory.create(
                Entry(api.request().response),
                self.params,
                self.params.type,
                self.width).run()
        if not self.params.raw:
            output = self.__format_output(output)
        return True, output

    def __indent(self, align):
        if align == Alignment.CENTER:
            return int((self.maxcol - self.width) / 2)
        elif align == Alignment.RIGHT:
            return self.maxcol - self.width
        return 0

    def __format_output(self, output):
        result = []
        for line in output.splitlines():
            result.extend(textwrap.wrap(line, self.width) if line else [''])
        result = textwrap.indent(
                "\n".join(result), ' ' * self.__indent(self.params.align))
        return result

    def __calculate_alignment(self):
        try:
            self.maxcol = os.get_terminal_size().columns
        except OSError:
            self.maxcol = ShowCommand.FAILWIDTH

        self.width = self.maxcol
        if self.params.width:
            if '%' in self.params.width:
                percent = int(self.params.width[:-1])
                self.width = int(self.width * percent / 100)
            else:
                self.width = int(self.params.width)
                if self.width > self.maxcol:
                    self.width = self.maxcol
