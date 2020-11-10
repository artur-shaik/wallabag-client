# -*- coding: utf-8 -*-

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
        result = (
                f'ID: {entry.entry_id}\n'
                f'Title: {entry.title}\n'
                f'Url: {entry.url}\n'
                f'Tags: {entry.get_tags_string()}\n'
                f'Is read: {entry.read}\n'
                f'Is starred: {entry.starred}\n'
                f'Created at: {entry.created_at.format_datetime()}\n'
                '{published_by}'
                f'Reading time: {entry.reading_time} min\n'
                '{preview_picture}')

        published_by = ""
        if entry.published_by:
            published_by = f'Published by: {",".join(entry.published_by)}\n'
        preview_picture = ""
        if entry.preview_picture:
            preview_picture = f'Preview picture: {entry.preview_picture}'

        return result.format(
                published_by=published_by, preview_picture=preview_picture)
