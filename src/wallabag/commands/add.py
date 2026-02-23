# -*- coding: utf-8 -*-

from colorama import Fore

from wallabag.api.add_entry import AddEntry, ApiMethod
from wallabag.api.add_entry import Params as AddEntryParams
from wallabag.api.entry_exists import EntryExists
from wallabag.commands.command import Command
from wallabag.commands.tags_param import TagsParam
from wallabag.commands.params import Params
from wallabag.entry import Entry


class AddCommandParams(Params, TagsParam):
    target_url = None
    title = None
    starred = None
    read = None
    tags = None
    return_url = None

    def __init__(
        self,
        target_url,
        title=None,
        starred=None,
        read=None,
        tags=None,
        return_url=None,
    ):
        self.target_url = target_url
        self.title = title
        self.starred = starred
        self.read = read
        self.tags = tags
        self.return_url = return_url

    def validate(self):
        return self._validate_tags()


class AddCommand(Command):

    def __init__(self, config, params=None):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        params = self.params
        api = EntryExists(self.config, params.target_url)
        response = api.request().response
        if "exists" in response and response["exists"] is not None:
            if self.params.return_url:
                return True, api._build_url(ApiMethod.VIEW).format(response["exists"])
            return True, "The url was already saved."

        entry = Entry(AddEntry(self.config, params.target_url, {
            AddEntryParams.TITLE: params.title,
            AddEntryParams.READ: params.read,
            AddEntryParams.STARRED: params.starred,
            AddEntryParams.TAGS: params.tags
        }).request().response)
        if self.params.return_url:
            return True, api._build_url(ApiMethod.VIEW).format(entry.entry_id)
        return True, (
                "Entry successfully added:\n\n"
                f"\t{Fore.GREEN}{entry.entry_id}. {entry.title}{Fore.RESET}\n")
