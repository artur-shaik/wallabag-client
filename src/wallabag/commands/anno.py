# -*- coding: utf-8 -*-

from enum import Enum, auto

import delorean
import humanize

from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.api.get_entry import GetEntry
from wallabag.api.api import ApiException
from wallabag.api.delete_annotation import DeleteAnnotation
from wallabag.entry import Entry


class AnnoSubcommand(Enum):
    LIST = auto()
    REMOVE = auto()

    def list():
        return [c.name for c in AnnoSubcommand]

    def get(name):
        for command in AnnoSubcommand:
            if command.name == name.upper():
                return command
        return AnnoSubcommand.LIST


class AnnoCommandParams(Params):
    command = AnnoSubcommand.LIST
    entry_id = None
    anno_id = None

    def validate(self):
        if self.command == AnnoSubcommand.LIST:
            if not self.entry_id:
                return False, 'Entry ID not specified'
        elif self.command == AnnoSubcommand.REMOVE:
            if not self.anno_id:
                return False, 'Annotation ID not specified.'
        return True, None


class AnnoCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        try:
            if self.params.command == AnnoSubcommand.LIST:
                api = GetEntry(self.config, self.params.entry_id)
                entry = Entry(api.request().response)
                result = []
                for anno in entry.annotations:
                    result.append(self.__get_anno_string(anno))

                return True, "\n".join(result)
            if self.params.command == AnnoSubcommand.REMOVE:
                DeleteAnnotation(self.config, self.params.anno_id).request()
                return True, 'Annotation successfully deleted'
        except ApiException as ex:
            return False, str(ex)
        return True, None

    def __get_anno_string(self, anno):
        past = delorean.utcnow() - delorean.parse(anno['updated_at'])
        return (f"{anno['id']}. {anno['quote']} "
                f"({humanize.naturaltime(past)}) [{len(anno['text'])}]")
