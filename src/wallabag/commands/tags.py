# -*- coding: utf-8 -*-

from wallabag.api.get_tags import GetTags
from wallabag.api.api import ApiException
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.command import Command


class TagsCommandParams():
    entry_id = None

    def __init__(self, entry_id=None):
        self.entry_id = entry_id


class TagsCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params if params else TagsCommandParams()

    def run(self):
        try:
            if self.params.entry_id:
                api = GetTagsForEntry(self.config, self.params.entry_id)
            else:
                api = GetTags(self.config)

            return True, self.__parse_tags(api.request().response)
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
