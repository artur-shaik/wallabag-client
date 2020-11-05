# -*- coding: utf-8 -*-

import pytest
import click

from colorama import Fore, Back

from tags import tags_test
from wallabag.config import Configs
from wallabag.api.add_tag_to_entry import AddTagToEntry
from wallabag.api.api import Response
from wallabag.api.api import RequestException
from wallabag.api.delete_tag_by_id import DeleteTagsById
from wallabag.api.delete_tags_by_label import DeleteTagsByLabel
from wallabag.api.delete_tag_from_entry import DeleteTagFromEntry
from wallabag.api.get_entry import GetEntry
from wallabag.api.get_list_entries import GetListEntries
from wallabag.api.get_tags import GetTags
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.tags import (
        TagsCommand, TagsCommandParams, TagsSubcommand)


class TestTags():

    def setup_method(self, method):
        self.config = Configs("/tmp/config")
        self.config.config.read_string("""
                [api]
                serverurl = url
                username = user
                password = pass
                [oauth2]
                client = 100
                secret = 100
                """)

    def test_list_tags(self, monkeypatch):

        def request(self):
            return Response(200, """[
            {"id": 3, "label": "book", "slug": "book"},
            {"id": 8, "label": "gut", "slug": "gut"},
            {"id": 7, "label": "security", "slug": "security"}]
            """)

        monkeypatch.setattr(GetTags, 'request', request)

        result, msg = TagsCommand(self.config).execute()
        assert result
        assert msg == '3. book\n7. security\n8. gut'

    def test_empty_tag_list(self, monkeypatch):

        def request(self):
            return Response(200, """[]""")

        monkeypatch.setattr(GetTags, 'request', request)

        result, msg = TagsCommand(self.config).execute()
        assert result
        assert not msg

    def test_list_entry_tags(self, monkeypatch):
        def request(self):
            return Response(200, """[
            {"id": 3, "label": "book", "slug": "book"},
            {"id": 8, "label": "gut", "slug": "gut"},
            {"id": 7, "label": "security", "slug": "security"}]
            """)

        monkeypatch.setattr(GetTagsForEntry, 'request', request)

        params = TagsCommandParams(entry_id=10)
        result, msg = TagsCommand(self.config, params).execute()
        assert result
        assert msg == '3. book\n7. security\n8. gut'

    def test_entry_not_found(self, monkeypatch):

        def request(self):
            response = Response(404, None)
            raise RequestException(
                    response.error_text, response.error_description)

        monkeypatch.setattr(GetTagsForEntry, 'request', request)

        params = TagsCommandParams(entry_id=10)
        result, msg = TagsCommand(self.config, params).execute()
        assert not result

    def test_add_tags_to_entry(self, monkeypatch):
        tag_to_entry_runned = False

        def request(self):
            nonlocal tag_to_entry_runned
            tag_to_entry_runned = True
            return Response(200, """[]""")

        monkeypatch.setattr(AddTagToEntry, 'request', request)

        params = TagsCommandParams(entry_id=10, tags='tag1')
        params.command = TagsSubcommand.ADD
        result, msg = TagsCommand(self.config, params).execute()
        assert tag_to_entry_runned
        assert result
        assert msg == 'Tags successfully added'

    @pytest.mark.parametrize('tags', tags_test)
    def test_tags_param(self, monkeypatch, tags):
        make_request_runned = False

        def request(self):
            nonlocal make_request_runned
            make_request_runned = True
            return Response(200, """[]""")

        monkeypatch.setattr(AddTagToEntry, 'request', request)

        params = TagsCommandParams(entry_id=10, tags=tags[0])
        params.configure(TagsSubcommand.ADD)
        result = TagsCommand(self.config, params).execute()
        if tags[0]:
            assert make_request_runned
            assert result[0]
            assert result[1] == "Tags successfully added"
        else:
            assert not make_request_runned
            assert not result[0]
            assert result[1] == "tags value is empty"

    def test_tags_to_entry_empty_id(self):
        params = TagsCommandParams(tags='tags')
        params.configure(TagsSubcommand.ADD)
        result = TagsCommand(self.config, params).execute()
        assert not result[0]
        assert result[1] == 'Entry id not specified'

    def test_remove_tag_from_entry_not_found(self, monkeypatch):

        def getentry_request(self):
            return Response(
                    200, (
                        '{"id": 1, "title": "title",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag1","slug":"tag1"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]}'))

        monkeypatch.setattr(GetEntry, 'request', getentry_request)

        params = TagsCommandParams(tags='tag', entry_id=1)
        params.configure(TagsSubcommand.REMOVE)
        result = TagsCommand(self.config, params).execute()
        assert not result[0]
        assert result[1] == 'Tag "tag" not found in entry:\n\n\ttitle\n'

    def test_remove_tag_from_entry(self, monkeypatch):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getentry_request(self):
            return Response(
                    200, (
                        '{"id": 1, "title": "title",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag","slug":"tag"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]}'))

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.RED}You are going to remove tag '
                    f'{Fore.BLUE}tag{Fore.RESET} from entry:'
                    f'{Back.RESET}\n\n\ttitle\n\nContinue?')

        monkeypatch.setattr(GetEntry, 'request', getentry_request)
        monkeypatch.setattr(DeleteTagFromEntry, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = TagsCommandParams(tags='tag', entry_id=1)
        params.configure(TagsSubcommand.REMOVE)
        result = TagsCommand(self.config, params).execute()
        assert confirm_runned
        assert result[0]

    @pytest.mark.parametrize('current_tag', ['tag', 'tag2'])
    def test_remove_tag_by_label(self, monkeypatch, current_tag):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getlist_request(self):
            return Response(
                    200, (
                        '{"_embedded": {"items": [{"id": 1, "title": "title",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag","slug":"tag"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]},'
                        '{"id": 2, "title": "title 2",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag","slug":"tag"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]}]}}'))

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.RED}You are going to remove tag '
                    f'{Fore.BLUE}{current_tag}{Fore.RESET} from this entries:'
                    f'{Back.RESET}\n\n\ttitle\n\ttitle 2\n\nContinue?')
            return True

        monkeypatch.setattr(GetListEntries, 'request', getlist_request)
        monkeypatch.setattr(DeleteTagsByLabel, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = TagsCommandParams(tags=current_tag)
        params.configure(TagsSubcommand.REMOVE)
        result = TagsCommand(self.config, params).execute()
        assert confirm_runned
        assert result[0]

    @pytest.mark.parametrize('tag_id', [1, '2'])
    def test_remove_tag_by_id(self, monkeypatch, tag_id):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.RED}You are going to remove tag with id: '
                    f'{Fore.BLUE}{int(tag_id)}{Fore.RESET}{Back.RESET}'
                    '\n\nContinue?')
            return True

        monkeypatch.setattr(DeleteTagsById, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = TagsCommandParams(tag_id=tag_id)
        params.configure(TagsSubcommand.REMOVE)
        result = TagsCommand(self.config, params).execute()
        assert confirm_runned
        assert result[0]
