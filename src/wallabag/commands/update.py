# -*- coding: utf-8 -*-

from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry, Params as UpdateEntryParams
from wallabag.entry import Entry


class UpdateCommandParams(Params):
    toggle_read = None
    toggle_star = None
    new_title = None
    set_read_state = None
    set_star_state = None
    force = False
    quiet = False
    check_toggle_options = True

    def __init__(self, check_toggle_options=True):
        self.check_toggle_options = check_toggle_options

    def validate(self):
        if self.set_star_state and self.toggle_star:
            self.toggle_star = None
        if self.set_read_state and self.toggle_read:
            self.toggle_read = None

        params = [
                not self.new_title,
                self.set_read_state is None,
                self.set_star_state is None
                ]
        if self.check_toggle_options:
            params.extend([not self.toggle_read, not self.toggle_star])

        for p in params:
            if not p:
                return True, None
        return False, 'No parameter given'


class UpdateCommand(Command):

    def __init__(self, config, entry_id, params):
        Command.__init__(self)
        self.config = config
        self.entry_id = entry_id
        self.params = params or UpdateCommandParams()

    def _run(self):
        params = self.params

        read_value = params.set_read_state
        star_value = params.set_star_state

        request = GetEntry(self.config, self.entry_id).request()
        entry = Entry(request.response)
        if params.toggle_read is not None and params.toggle_read:
            read_value = not entry.read
        if params.toggle_star is not None and params.toggle_star:
            star_value = not entry.starred

        request = UpdateEntry(self.config, self.entry_id, {
            UpdateEntryParams.TITLE: params.new_title,
            UpdateEntryParams.STAR: star_value,
            UpdateEntryParams.READ: read_value
        }).request()
        if not params.quiet:
            return True, "Entry successfully updated."
        return True, None
