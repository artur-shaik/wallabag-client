# -*- coding: utf-8 -*-

import click
from colorama import Back

from wallabag.api.api import ApiException
from wallabag.api.get_entry import GetEntry
from wallabag.api.delete_entry import DeleteEntry
from wallabag.commands.command import Command
from wallabag.entry import Entry


class DeleteCommandParams():

    def __init__(self, entry_id, force=False, quiet=False):
        self.entry_id = entry_id
        self.force = force
        self.quiet = quiet


class DeleteCommand(Command):

    WARN_MSG = 'You are going to remove the following entry'

    def __init__(self, config, params):
        self.config = config
        self.params = params or DeleteCommandParams()

    def run(self):
        if not self.params.force:
            try:
                request = GetEntry(self.config, self.params.entry_id).request()
                entr = Entry(request.response)
                confirm_msg = (
                        f"{Back.RED}{DeleteCommand.WARN_MSG}:{Back.RESET}\n\n"
                        f"\t{entr.title}\n\n"
                        "Continue?")
                if not click.confirm(confirm_msg):
                    return True, 'Cancelling'
            except ApiException as ex:
                return False, str(ex)

        try:
            request = DeleteEntry(self.config, self.params.entry_id).request()
            if not self.params.quiet:
                return True, "Entry successfully deleted."
            return True, None
        except ApiException as ex:
            return False, str(ex)
