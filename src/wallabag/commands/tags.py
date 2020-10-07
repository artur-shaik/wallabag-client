# -*- coding: utf-8 -*-

from wallabag.api.get_tags import GetTags
from wallabag.api.api import ApiException
from wallabag.commands.command import Command


class TagsCommand(Command):

    def __init__(self, config):
        self.config = config

    def run(self):
        try:
            response = GetTags(self.config).request().response
            return True, self.__parse_tags(response)
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
