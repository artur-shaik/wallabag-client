# -*- coding: utf-8 -*-

import os
from datetime import datetime
from enum import Enum, auto
from pathlib import PurePath, Path

from wallabag.commands.params import Params
from wallabag.commands.command import Command
from wallabag.api.export_entry import ExportEntry


class FormatType(Enum):
    XML = auto()
    JSON = auto()
    TXT = auto()
    CSV = auto()
    PDF = auto()
    EPUB = auto()
    MOBI = auto()
    HTML = auto()

    def list():
        return [c.name for c in FormatType]

    def get(name):
        for format in FormatType:
            if format.name == name.upper():
                return format
        return FormatType.JSON


class ExportCommandParams(Params):
    entry_id = None
    format = None
    output_file = None

    def __init__(
            self, entry_id, format: FormatType, output_file: PurePath = None):
        self.entry_id = entry_id
        self.format = format
        self.output_file = output_file

    def validate(self):
        try:
            if not self.entry_id or int(self.entry_id) < 0:
                return False, 'Entry ID not specified'
        except ValueError:
            return False, 'Wrong Entry ID value'

        if not self.format:
            return False, 'Format type not specified'

        if not self.output_file:
            self.output_file = Path.cwd()

        return True, None


class ExportCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        format = self.params.format.name.lower()
        result = ExportEntry(
                self.config,
                self.params.entry_id,
                format).request()
        if os.path.isdir(self.params.output_file):
            new_name = result.filename if result.filename else str(
                    f'{datetime.now().timestamp()}.{format}')
            self.params.output_file = PurePath(
                    f'{self.params.output_file}/{new_name}')
        with open(self.params.output_file, 'wb') as file:
            file.write(result.content)
        return True, f'Exported to: {self.params.output_file}'
