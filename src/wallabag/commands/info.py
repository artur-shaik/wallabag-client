# -*- coding: utf-8 -*-

from colorama import Fore

from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.entry import Entry
from wallabag.api.get_entry import GetEntry


class InfoCommandParams(Params):
    entry_id = None

    def __init__(self, entry_id):
        self.entry_id = entry_id

    def validate(self):
        if not self.entry_id:
            return False, 'Entry ID not specified'
        return True, None


class InfoCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params if params else InfoCommandParams(None)

    def _run(self):
        entry = Entry(
                GetEntry(
                    self.config, self.params.entry_id).request().response)
        return True, self.__entry_to_string(entry)

    def __entry_to_string(self, entry):
        f_c = Fore.LIGHTBLUE_EX
        f_rst = Fore.RESET

        published_by = ""
        if entry.published_by:
            published_by = (
                    f'{f_c}Published by{f_rst}: '
                    f'{",".join(entry.published_by)}\n')
        preview_picture = ""
        if entry.preview_picture:
            preview_picture = (
                    f'{f_c}Preview picture{f_rst}: '
                    f'{entry.preview_picture}')

        tags = ""
        if entry.tags:
            tags = f'{f_c}Tags{f_rst}: {entry.get_tags_string()}\n'

        annotations = ""
        if entry.annotations:
            annotations =\
                f'{f_c}Annotations{f_rst}: {len(entry.annotations)}\n'

        return (
                f'{f_c}ID{f_rst}: {entry.entry_id}\n'
                f'{f_c}Title{f_rst}: {entry.title}\n'
                f'{f_c}Url{f_rst}: {entry.url}\n'
                f'{annotations}'
                f'{tags}'
                f'{f_c}Is read{f_rst}: {entry.read}\n'
                f'{f_c}Is starred{f_rst}: {entry.starred}\n'
                f'{f_c}Created at{f_rst}: '
                f'{entry.created_at.format_datetime()}\n'
                f'{published_by}'
                f'{f_c}Reading time{f_rst}: {entry.reading_time} min\n'
                f'{preview_picture}')
