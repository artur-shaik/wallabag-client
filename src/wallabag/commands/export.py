# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import PurePath, Path

from wallabag.commands.params import Params
from wallabag.commands.command import Command
from wallabag.api.export_entry import ExportEntry
from wallabag.api.get_entry import GetEntry
from wallabag.entry import Entry
from wallabag.format_type import FormatType, ScreenType, format_to_screen
from wallabag.export.export_factory import ExportFactory


class ExportCommandParams(Params):
    entry_id = None
    type = None
    output_file = None
    filename_with_id = True

    def __init__(
            self, entry_id, type: FormatType, output_file: PurePath = None):
        self.entry_id = entry_id
        self.type = type
        self.output_file = output_file

    def validate(self):
        try:
            if not self.entry_id or int(self.entry_id) < 0:
                return False, 'Entry ID not specified'
        except ValueError:
            return False, 'Wrong Entry ID value'

        if not self.type:
            return False, 'Type not specified'

        if self.type == FormatType.UNSUPPORTED:
            return False, 'Unsupported type'

        if not self.output_file:
            self.output_file = Path.cwd()

        return True, None


class ExportCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        type = self.params.type
        output_file = self.params.output_file
        extension = FormatType.extension(type)
        result = self.__get_result(type, extension)
        output_file = self.__check_output_file(result, output_file, extension)
        self.__create_output_path(output_file)
        self.__fix_file_name(result, extension)
        output_file = PurePath(
                f'{Path(output_file).resolve()}/'
                f'{self.__get_filename(result.filename)}')

        with open(output_file, 'wb') as file:
            file.write(result.content)
        return True, f'Exported to: {output_file}'

    def __get_result(self, type, extension):
        if type.name in ScreenType.list():
            result = GetEntry(
                        self.config,
                        self.params.entry_id).request()
            entry = Entry(result.response)
            result.filename = f'{entry.title}.{extension}'
            result.content = bytes(ExportFactory.create(
                    entry, None, format_to_screen(type), None).run(), 'utf-8')
        else:
            result = ExportEntry(
                    self.config,
                    self.params.entry_id,
                    type.name.lower()).request()
        return result

    def __check_output_file(self, result, output_file, extension):
        if output_file.name.endswith(f'.{extension}'):
            result.filename = output_file.name
            output_file = output_file.parent
        return output_file

    def __create_output_path(self, output_file):
        if not Path(output_file).exists():
            Path(output_file).mkdir(parents=True)

    def __fix_file_name(self, result, extension):
        if not result.filename or result.filename.startswith('.'):
            entry = Entry(
                GetEntry(
                    self.config,
                    self.params.entry_id).request().response)
            result.filename = f'{entry.title}.{extension}'

    def __get_filename(self, name):
        if self.params.filename_with_id:
            return f'{self.params.entry_id}. {name}'
        return name
