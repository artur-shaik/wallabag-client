# -*- coding: utf-8 -*-

import click
from colorama import Fore, Back

from wallabag.api.get_list_entries import GetListEntries, Params as ListParams
from wallabag.commands.command import Command
from wallabag.commands.update import UpdateCommandParams
from wallabag.api.update_entry import UpdateEntry, Params
from wallabag.entry import Entry
from wallabag import wclick


class UpdateByTagsCommand(Command):

    def __init__(self, config, tags, params):
        Command.__init__(self)
        self.config = config
        self.tags = tags
        self.params = params or UpdateCommandParams(False)

        self.__updating_list = []

    def _run(self):
        params = self.params

        api = GetListEntries(self.config, {
            ListParams.TAGS: self.tags,
            ListParams.COUNT: 100
        })
        entries = Entry.create_list(
                api.request().response['_embedded']["items"])
        if not params.force:
            titles = "\n\t".join([x.title for x in entries])
            confirm_msg = (
                    f'{Back.GREEN}You are going to update '
                    f'{self.__get_update_status()} '
                    f'of followed entries:{Back.RESET}'
                    f'\n\n\t{titles}\n\nContinue?')
            if not wclick.confirm(confirm_msg):
                return True, 'Cancelling'

        for entry in entries:
            self.__log(entry.title)
            UpdateEntry(self.config, entry.entry_id, {
                Params.STAR: self.params.set_star_state,
                Params.READ: self.params.set_read_state
            }).request()
            self.__log(entry.title)

        return True, None

    def __get_update_status(self):
        result = ""
        if self.params.set_read_state is not None:
            result = "read status to "
            if self.params.set_read_state:
                result += "read"
            else:
                result += "not read"
        if self.params.set_star_state is not None:
            if result:
                result += " and "
            result += "starred status to "
            if self.params.set_star_state:
                result += "starred"
            else:
                result += "unstarred"
        return result

    def __log(self, title):
        if self.params.quiet:
            return
        if title not in self.__updating_list:
            click.echo(f'Updating entry: {title}', nl=False)
            self.__updating_list.append(title)
        else:
            click.echo(f'\t...\t{Fore.GREEN}success{Fore.RESET}')
