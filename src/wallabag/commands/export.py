# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum, auto
from pathlib import PurePath, Path

from wallabag.commands.params import Params
from wallabag.commands.command import Command
from wallabag.api.export_entry import ExportEntry
from wallabag.api.get_entry import GetEntry
from wallabag.entry import Entry


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
    filename_with_id = True

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
        output_file = self.params.output_file
        result = ExportEntry(
                self.config,
                self.params.entry_id,
                format).request()
        if output_file.name.endswith(f'.{format}'):
            result.filename = output_file.name
            output_file = output_file.parent
        if not Path(output_file).exists():
            Path(output_file).mkdir(parents=True)
        if result.filename:
            if result.filename.startswith('.'):
                entry = Entry(
                        GetEntry(
                            self.config,
                            self.params.entry_id).request().response)
                result.filename = f'{entry.title}{result.filename}'
            new_name = result.filename
        else:
            new_name = str(f'{datetime.now().timestamp()}.{format}')
        output_file = PurePath(
                f'{Path(output_file).resolve()}/'
                f'{self.__get_filename(new_name)}')

        with open(output_file, 'wb') as file:
            file.write(result.content)
        return True, f'Exported to: {output_file}'

    def __get_filename(self, name):
        if self.params.filename_with_id:
            return f'{self.params.entry_id}. {name}'
        return name
