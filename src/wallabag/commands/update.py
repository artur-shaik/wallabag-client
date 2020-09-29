# -*- coding: utf-8 -*-

from wallabag.api.api import ApiException
from wallabag.commands.command import Command
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry, Params
from wallabag.entry import Entry


class UpdateCommandParams():
    entry_id = None
    toggle_read = False
    toggle_star = False
    new_title = None
    quiet = False

    def __init__(self, entry_id):
        self.entry_id = entry_id

    def validate(self):
        if not self.new_title and not self.toggle_read\
                and not self.toggle_star:
            return False
        return True


class UpdateCommand(Command):

    def __init__(self, config, params):
        self.config = config
        self.params = params or UpdateCommandParams()

    def run(self):
        params = self.params
        if not params.validate():
            return False, "Error: No parameter given."

        read_value = None
        star_value = None

        try:
            request = GetEntry(self.config, params.entry_id).request()
            entry = Entry(request.response)
            if params.toggle_read:
                read_value = not entry.read
            if params.toggle_star:
                star_value = not entry.starred
        except ApiException as ex:
            return False, str(ex)

        try:
            request = UpdateEntry(self.config, params.entry_id, {
                Params.TITLE: params.new_title,
                Params.STAR: star_value,
                Params.READ: read_value
            }).request()
            if not params.quiet:
                return True, "Entry successfully updated."
        except ApiException as ex:
            return False, str(ex)
