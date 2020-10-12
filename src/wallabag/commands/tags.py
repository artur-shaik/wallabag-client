# -*- coding: utf-8 -*-

from enum import Enum, auto

import click
from colorama import Fore, Back

from wallabag.api.add_tag_to_entry import AddTagToEntry, Params
from wallabag.api.get_tags import GetTags
from wallabag.api.api import ApiException
from wallabag.api.delete_tag_from_entry import DeleteTagFromEntry
from wallabag.api.get_entry import GetEntry
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.command import Command
from wallabag.commands.tags_param import TagsParam
from wallabag.entry import Entry


class TagsSubcommand(Enum):
    LIST = auto()
    ADD = auto()
    REMOVE = auto()

    def list():
        return [c.name for c in TagsSubcommand]

    def get(name):
        for command in TagsSubcommand:
            if command.name == name.upper():
                return command
        return TagsSubcommand.LIST


class ValidateError(Exception):
    pass


class TagsCommandParams(TagsParam):
    command = TagsSubcommand.LIST
    entry_id = None
    tags = None

    def __init__(self, entry_id=None, tags=None):
        self.entry_id = entry_id
        self.tags = tags

    def validate(self):
        result, msg = self._validate_tags()
        if not result:
            raise ValidateError(msg)
        elif not self.entry_id:
            raise ValidateError('Entry id not specified')


class TagsCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params if params else TagsCommandParams()

        self.runner = {
            TagsSubcommand.LIST: self.__subcommand_list,
            TagsSubcommand.ADD: self.__subcommand_add,
            TagsSubcommand.REMOVE: self.__subcommand_remove
        }

    def run(self):
        return self.runner[self.params.command]()

    def __subcommand_list(self):
        try:
            if self.params.entry_id:
                api = GetTagsForEntry(self.config, self.params.entry_id)
            else:
                api = GetTags(self.config)

            return True, self.__parse_tags(api.request().response)
        except ApiException as ex:
            return False, str(ex)

    def __subcommand_add(self):
        try:
            self.params.validate()
            AddTagToEntry(self.config, {
                Params.ENTRY_ID: self.params.entry_id,
                Params.TAGS: self.params.tags
            }).request()

            return True, 'Tags successfully added'
        except (ValidateError, ApiException) as ex:
            return False, str(ex)

    def __subcommand_remove(self):
        try:
            self.params.validate()
            api = GetEntry(self.config, self.params.entry_id)
            entry = Entry(api.request().response)
            tag = list(filter(
                    lambda t: t['slug'] == self.params.tags,
                    entry.tags))
            if not tag:
                return False, (
                        f'Tag "{self.params.tags}" not found '
                        f'in entry:\n\n\t{entry.title}\n')
            tag = tag[0]

            confirm_msg = (
                    f'{Back.RED}You are going to remove tag '
                    f'{Fore.BLUE}{self.params.tags}{Fore.RESET} from entry:'
                    f'{Back.RESET}'
                    f'\n\n\t{entry.title}\n\n'
                    'Continue?')
            if not click.confirm(confirm_msg):
                return True, 'Cancelling'

            DeleteTagFromEntry(
                    self.config, self.params.entry_id,
                    tag['id']).request()
        except (ValidateError, ApiException) as ex:
            return False, str(ex)
        return True, None

    def __parse_tags(self, response):
        def sort(tag):
            return int(tag['id'])

        return "\n".join(
                map(
                    lambda tag: self.__tag_format(tag),
                    sorted(response, key=sort)))

    def __tag_format(self, tag):
        return f"{tag['id']}. {tag['slug']}"
