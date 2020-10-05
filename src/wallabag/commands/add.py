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
    tags = None

    def __init__(self, target_url, title=None,
                 starred=None, read=None, tags=None):
        self.target_url = target_url
        self.title = title
        self.starred = starred
        self.read = read
        self.tags = tags

    def validate(self):
        if self.tags is not None:
            used = set()
            self.tags = ",".join([x.strip() for x in self.tags.split(',')
                                  if x.strip() and x not in used and
                                  (used.add(x) or True)])
            if not self.tags:
                return False, 'tags value is empty'
        return True, None


class AddCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params

    def run(self):
        params = self.params
        validated, error = params.validate()
        if not validated:
            return False, error

        try:
            api = EntryExists(self.config, params.target_url)
            if api.request().response['exists']:
                return True, "The url was already saved."

            AddEntry(self.config, params.target_url, {
                Params.TITLE: params.title,
                Params.READ: params.read,
                Params.STARRED: params.starred,
                Params.TAGS: params.tags
            }).request()
            return True, "Entry successfully added."
        except ApiException as ex:
            return False, str(ex)
