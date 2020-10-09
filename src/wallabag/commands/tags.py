# -*- coding: utf-8 -*-

from enum import Enum, auto

from wallabag.api.add_tag_to_entry import AddTagToEntry, Params
from wallabag.api.get_tags import GetTags
from wallabag.api.api import ApiException
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.command import Command
from wallabag.commands.tags_param import TagsParam


class TagsSubcommand(Enum):
    LIST = auto()
    ADD = auto()


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
            return False, msg
        elif not self.entry_id:
            return False, 'Entry id not specified'
        return True, None


class TagsCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params if params else TagsCommandParams()

        self.runner = {
            TagsSubcommand.LIST: self.__subcommand_list,
            TagsSubcommand.ADD: self.__subcommand_add
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
        validated, error = self.params.validate()
        if not validated:
            return False, error
        try:
            AddTagToEntry(self.config, {
                Params.ENTRY_ID: self.params.entry_id,
                Params.TAGS: self.params.tags
            }).request()

            return True, 'Tags successfully added'
        except ApiException as ex:
            return False, str(ex)

    def __parse_tags(self, response):
        def sort(tag):
            return int(tag['id'])

        return "\n".join(
                map(
                    lambda tag: self.__tag_format(tag),
                    sorted(response, key=sort)))

    def __tag_format(self, tag):
        return f"{tag['id']}. {tag['slug']}"
