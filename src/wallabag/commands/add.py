# -*- coding: utf-8 -*-

from wallabag.api.api import ApiException
from wallabag.api.add_entry import AddEntry, Params
from wallabag.api.entry_exists import EntryExists
from wallabag.commands.command import Command


class AddCommandParams():
    target_url = None
    title = None
    starred = None
    read = None

    def __init__(self, target_url, title=None, starred=None, read=None):
        self.target_url = target_url
        self.title = title
        self.starred = starred
        self.read = read


class AddCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params

    def run(self):
        params = self.params
        try:
            api = EntryExists(self.config, params.target_url)
            if api.request().response['exists']:
                return True, "The url was already saved."

            AddEntry(self.config, params.target_url, {
                Params.TITLE: params.title,
                Params.READ: params.read,
                Params.STARRED: params.starred
            }).request()
            return True, "Entry successfully added."
        except ApiException as ex:
            return False, str(ex)
