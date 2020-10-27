# -*- coding: utf-8 -*-

from wallabag.api.api import ApiException
from wallabag.api.add_entry import AddEntry, Params as AddEntryParams
from wallabag.api.entry_exists import EntryExists
from wallabag.commands.command import Command
from wallabag.commands.tags_param import TagsParam
from wallabag.commands.params import Params


class AddCommandParams(Params, TagsParam):
    target_url = None
    title = None
    starred = None
    read = None
    tags = None

    def __init__(self, target_url, title=None,
                 starred=None, read=None, tags=None):
        self.target_url = target_url
        self.title = title
        self.starred = starred
        self.read = read
        self.tags = tags

    def validate(self):
        return self._validate_tags()


class AddCommand(Command):

    def __init__(self, config, params=None):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        params = self.params
        try:
            api = EntryExists(self.config, params.target_url)
            if api.request().response['exists']:
                return True, "The url was already saved."

            AddEntry(self.config, params.target_url, {
                AddEntryParams.TITLE: params.title,
                AddEntryParams.READ: params.read,
                AddEntryParams.STARRED: params.starred,
                AddEntryParams.TAGS: params.tags
            }).request()
            return True, "Entry successfully added."
        except ApiException as ex:
            return False, str(ex)
