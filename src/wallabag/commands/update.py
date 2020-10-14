# -*- coding: utf-8 -*-

from wallabag.api.api import ApiException
from wallabag.commands.command import Command
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry, Params
from wallabag.entry import Entry


class UpdateCommandParams():
    toggle_read = None
    toggle_star = None
    new_title = None
    set_read_state = None
    set_star_state = None
    force = False
    quiet = False

    def __init__(self, toggle_read=None, toggle_star=None, new_title=None):
        self.toggle_read = toggle_read
        self.toggle_star = toggle_star
        self.new_title = new_title

    def validate(self, check_toggle_options=True):
        if self.set_star_state and self.toggle_star:
            self.toggle_star = None
        if self.set_read_state and self.toggle_read:
            self.toggle_read = None

        params = [
                not self.new_title,
                self.set_read_state is None,
                self.set_star_state is None
                ]
        if check_toggle_options:
            params.extend([not self.toggle_read, not self.toggle_star])

        for p in params:
            if not p:
                return True
        raise ValueError('No parameter given')


class UpdateCommand(Command):

    def __init__(self, config, entry_id, params):
        self.config = config
        self.entry_id = entry_id
        self.params = params or UpdateCommandParams()

    def run(self):
        params = self.params

        read_value = params.set_read_state
        star_value = params.set_star_state

        try:
            params.validate()
            request = GetEntry(self.config, self.entry_id).request()
            entry = Entry(request.response)
            if params.toggle_read is not None and params.toggle_read:
                read_value = not entry.read
            if params.toggle_star is not None and params.toggle_star:
                star_value = not entry.starred

            request = UpdateEntry(self.config, self.entry_id, {
                Params.TITLE: params.new_title,
                Params.STAR: star_value,
                Params.READ: read_value
            }).request()
            if not params.quiet:
                return True, "Entry successfully updated."
        except (ValueError, ApiException) as ex:
            return False, str(ex)
