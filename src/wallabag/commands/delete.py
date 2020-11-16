# -*- coding: utf-8 -*-

from colorama import Back

from wallabag.api.get_entry import GetEntry
from wallabag.api.delete_entry import DeleteEntry
from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.entry import Entry
from wallabag import wclick


class DeleteCommandParams(Params):

    def __init__(self, entry_id, force=False, quiet=False):
        self.entry_id = entry_id
        self.force = force
        self.quiet = quiet


class DeleteCommand(Command):

    WARN_MSG = 'You are going to remove the following entry'

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params or DeleteCommandParams()

    def _run(self):
        if not self.params.force:
            request = GetEntry(self.config, self.params.entry_id).request()
            entr = Entry(request.response)
            confirm_msg = (
                    f"{Back.RED}{DeleteCommand.WARN_MSG}:{Back.RESET}\n\n"
                    f"\t{entr.title}\n\n"
                    "Continue?")
            if not wclick.confirm(confirm_msg):
                return True, 'Cancelling'

        request = DeleteEntry(self.config, self.params.entry_id).request()
        if not self.params.quiet:
            return True, "Entry successfully deleted."
        return True, None
