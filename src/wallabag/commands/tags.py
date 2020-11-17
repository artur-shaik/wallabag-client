# -*- coding: utf-8 -*-

from enum import Enum, auto

from colorama import Fore, Back

from wallabag.api.add_tag_to_entry import AddTagToEntry, Params as AddTagParams
from wallabag.api.get_tags import GetTags
from wallabag.api.delete_tag_from_entry import DeleteTagFromEntry
from wallabag.api.get_entry import GetEntry
from wallabag.api.get_list_entries import GetListEntries, Params as ListParams
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.api.delete_tag_by_id import DeleteTagsById
from wallabag.api.delete_tags_by_label import DeleteTagsByLabel
from wallabag.commands.command import Command
from wallabag.commands.tags_param import TagsParam
from wallabag.commands.params import Params
from wallabag.entry import Entry
from wallabag import wclick


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


class RemoveSubcommand(Enum):
    FROM_ENTRY = auto()
    BY_TAG_ID = auto()
    BY_TAG_NAME = auto()


class TagsCommandParams(Params, TagsParam):
    command = TagsSubcommand.LIST
    remove_command = None
    entry_id = None
    tag_id = None
    tags = None
    validate_tags = False
    validate_entry_id = False
    validate_tag_id = False

    config = {TagsSubcommand.LIST: (False, False, False),
              TagsSubcommand.ADD: (True, True, False),
              TagsSubcommand.REMOVE: {
                  RemoveSubcommand.FROM_ENTRY: (True, True, False),
                  RemoveSubcommand.BY_TAG_ID: (False, False, True),
                  RemoveSubcommand.BY_TAG_NAME: (True, False, False)
              }}

    def __init__(self, entry_id=None, tags=None, tag_id=None):
        self.entry_id = entry_id
        self.tags = tags
        self.tag_id = tag_id

    def configure(self, command):
        self.command = command
        result = self.config[command]
        if self.command == TagsSubcommand.REMOVE:
            if self.entry_id:
                self.remove_command = RemoveSubcommand.FROM_ENTRY
            elif self.tag_id:
                self.remove_command = RemoveSubcommand.BY_TAG_ID
            else:
                self.remove_command = RemoveSubcommand.BY_TAG_NAME
            result = result[self.remove_command]

        self.validate_tags = result[0]
        self.validate_entry_id = result[1]
        self.validate_tag_id = result[2]

    def validate(self, tags=False, entry_id=False, tag_id=False):
        if self.validate_tags:
            result, msg = self._validate_tags()
            if not result:
                return False, msg
        if self.validate_entry_id and not self.entry_id:
            return False, 'Entry id not specified'
        if self.validate_tag_id:
            if self.tag_id:
                try:
                    self.tag_id = int(self.tag_id)
                except ValueError:
                    return False, 'Tag id is not integer'
            else:
                return False, 'Tag id is not set'
        return True, None


class TagsCommand(Command):

    def __init__(self, config, params=None):
        Command.__init__(self)
        self.config = config
        self.params = params if params else TagsCommandParams()

        self.runner = {
            TagsSubcommand.LIST: self.__subcommand_list,
            TagsSubcommand.ADD: self.__subcommand_add,
            TagsSubcommand.REMOVE: self.__subcommand_remove
        }

    def _run(self):
        return self.runner[self.params.command]()

    def __subcommand_list(self):
        if self.params.entry_id:
            api = GetTagsForEntry(self.config, self.params.entry_id)
        else:
            api = GetTags(self.config)

        return True, self.__parse_tags(api.request().response)

    def __subcommand_add(self):
        AddTagToEntry(self.config, {
            AddTagParams.ENTRY_ID: self.params.entry_id,
            AddTagParams.TAGS: self.params.tags
        }).request()

        return True, 'Tags successfully added'

    def __subcommand_remove(self):
        remove = {
                RemoveSubcommand.FROM_ENTRY: self.__remove_from_entry,
                RemoveSubcommand.BY_TAG_ID: self.__remove_by_tag_id,
                RemoveSubcommand.BY_TAG_NAME: self.__remove_by_tag_name
        }
        if self.params.remove_command not in remove:
            return False, 'Command not found'
        return remove[self.params.remove_command]()

    def __remove_by_tag_id(self):
        confirm_msg = (
                f'{Back.RED}You are going to remove tag with id: '
                f'{Fore.BLUE}{self.params.tag_id}{Fore.RESET}{Back.RESET}'
                '\n\nContinue?')
        if not wclick.confirm(confirm_msg):
            return True, 'Cancelling'

        DeleteTagsById(self.config, self.params.tag_id).request()
        return True, None

    def __remove_by_tag_name(self):
        entries = list()
        for tag in self.params.tags.split(','):
            api = GetListEntries(self.config, {
                ListParams.TAGS: tag,
                ListParams.COUNT: 100
            })
            entries.extend(Entry.create_list(
                    api.request().response['_embedded']["items"]))
        titles = "\n\t".join([x.title for x in entries])
        confirm_msg = (
                f'{Back.RED}You are going to remove tag '
                f'{Fore.BLUE}{self.params.tags}{Fore.RESET} '
                f'from this entries:{Back.RESET}\n\n\t{titles}'
                '\n\nContinue?')
        if not wclick.confirm(confirm_msg):
            return True, 'Cancelling'

        DeleteTagsByLabel(self.config, self.params.tags).request()
        return True, None

    def __remove_from_entry(self):
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
        if not wclick.confirm(confirm_msg):
            return True, 'Cancelling'

        DeleteTagFromEntry(
                self.config, self.params.entry_id,
                tag['id']).request()
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
