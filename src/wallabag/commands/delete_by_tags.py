# -*- coding: utf-8 -*-

import click
from colorama import Fore, Back

from wallabag.commands.tags_param import TagsParam
from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.api.api import ApiException
from wallabag.api.get_list_entries import (
        GetListEntries, Params as ListEntriesParams)
from wallabag.api.delete_entry import DeleteEntry
from wallabag.entry import Entry


class DeleteByTagsParams(Params, TagsParam):
    tags = None
    force = None
    quiet = None

    def __init__(self, tags, force=False, quiet=False):
        self.tags = tags
        self.force = force
        self.quiet = quiet

    def validate(self):
        return self._validate_tags()


class DeleteByTags(Command):

    def __init__(self, config, params=None):
        Command.__init__(self)
        self.config = config
        self.params = params if params else DeleteByTagsParams()

    def _run(self):
        try:
            api = GetListEntries(self.config, {
                ListEntriesParams.TAGS: self.params.tags,
                ListEntriesParams.COUNT: 100
            })
            entries = Entry.create_list(
                    api.request().response['_embedded']["items"])
            if not self.params.force:
                titles = "\n\t".join([x.title for x in entries])
                confirm_msg = (
                        f'{Back.RED}You are going to remove '
                        f'followed entries:{Back.RESET}'
                        f'\n\n\t{titles}\n\nContinue?')
                if not click.confirm(confirm_msg):
                    return True, 'Cancelling'

            for entry in entries:
                if not self.params.quiet:
                    click.echo(f'Deleting entry: {entry.title}', nl=False)
                DeleteEntry(self.config, entry.entry_id).request()
                if not self.params.quiet:
                    click.echo(f'\t...\t{Fore.GREEN}success{Fore.RESET}')

            return True, None
        except ApiException as err:
            return False, str(err)
