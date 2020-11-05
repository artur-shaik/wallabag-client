# -*- coding: utf-8 -*-

from enum import Enum, auto

import delorean
import humanize

from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.api.get_entry import GetEntry
from wallabag.api.delete_annotation import DeleteAnnotation
from wallabag.entry import Entry


class AnnoSubcommand(Enum):
    LIST = auto()
    REMOVE = auto()
    SHOW = auto()

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
        if self.command in (AnnoSubcommand.LIST, AnnoSubcommand.SHOW):
            if not self.entry_id:
                return False, 'Entry ID not specified'
        elif self.command == AnnoSubcommand.REMOVE:
            if not self.anno_id:
                return False, 'Annotation ID not specified'
        return True, None


class AnnoCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

        self.__get_anno = {
                AnnoSubcommand.LIST: self.__get_anno_string,
                AnnoSubcommand.SHOW: self.__get_anno_full
        }

    def _run(self):
        params = self.params
        if params.command in (AnnoSubcommand.LIST, AnnoSubcommand.SHOW):
            api = GetEntry(self.config, params.entry_id)
            entry = Entry(api.request().response)
            result = []
            for anno in sorted(
                    entry.annotations, key=lambda x: int(x['id'])):
                result.append(self.__get_anno[params.command](anno))
            return True, "\n".join(filter(None, result))
        if params.command == AnnoSubcommand.REMOVE:
            DeleteAnnotation(self.config, self.params.anno_id).request()
            return True, 'Annotation successfully deleted'
        return False, "Unknown command"

    def __get_anno_string(self, anno):
        past = delorean.utcnow() - delorean.parse(anno['updated_at'])
        return (f"{anno['id']}. {anno['quote']} "
                f"({humanize.naturaltime(past)}) [{len(anno['text'])}]")

    def __get_anno_full(self, anno):
        if self.params.anno_id:
            if self.params.anno_id != int(anno['id']):
                return ""
        past = delorean.utcnow() - delorean.parse(anno['updated_at'])
        return (f"{anno['id']}. {anno['quote']} "
                f"({humanize.naturaltime(past)}):\n\n\t{anno['text']}\n")
