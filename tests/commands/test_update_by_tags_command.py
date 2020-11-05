# -*- coding: utf-8 -*-

import click
import pytest

from colorama import Back

from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.update_entry import UpdateEntry
from wallabag.api.get_list_entries import GetListEntries
from wallabag.commands.update import UpdateCommandParams
from wallabag.commands.update_by_tags import UpdateByTagsCommand


class TestUpdateByTags():

    entries_list_response = (
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
            '{"id":13,"label":"tag2","slug":"tag2"}]}]}}')

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

    def test_update_entries(self, monkeypatch):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getlist_request(self):
            return Response(200, TestUpdateByTags.entries_list_response)

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.GREEN}You are going to update read status to read '
                    f'of followed entries:{Back.RESET}'
                    f'\n\n\ttitle\n\ttitle 2\n\nContinue?')
            return True

        monkeypatch.setattr(GetListEntries, 'request', getlist_request)
        monkeypatch.setattr(UpdateEntry, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = UpdateCommandParams(False)
        params.set_read_state = True
        result = UpdateByTagsCommand(self.config, 'tag,tag2', params).execute()
        assert confirm_runned
        assert result[0]

    @pytest.mark.parametrize('values', [
        ((True, False), (False, False), "read status to not read"),
        ((True, True), (False, False), "read status to read"),
        ((False, False), (True, False), "starred status to unstarred"),
        ((False, False), (True, True), "starred status to starred"),
        ((True, False), (True, True),
            "read status to not read and starred status to starred"),
        ((True, True), (True, True),
            "read status to read and starred status to starred"),
        ((True, True), (True, False),
            "read status to read and starred status to unstarred"),
        ])
    def test_confirm_messages(self, monkeypatch, values):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getlist_request(self):
            return Response(200, TestUpdateByTags.entries_list_response)

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.GREEN}You are going to update {values[2]} '
                    f'of followed entries:{Back.RESET}'
                    f'\n\n\ttitle\n\ttitle 2\n\nContinue?')
            return True

        monkeypatch.setattr(GetListEntries, 'request', getlist_request)
        monkeypatch.setattr(UpdateEntry, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = UpdateCommandParams(False)
        if values[0][0]:
            params.set_read_state = values[0][1]
        if values[1][0]:
            params.set_star_state = values[1][1]
        result = UpdateByTagsCommand(self.config, 'tag,tag2', params).execute()
        assert confirm_runned
        assert result[0]

    def test_force_param(self, monkeypatch):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getlist_request(self):
            return Response(200, TestUpdateByTags.entries_list_response)

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            return True

        monkeypatch.setattr(GetListEntries, 'request', getlist_request)
        monkeypatch.setattr(UpdateEntry, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = UpdateCommandParams(False)
        params.set_read_state = True
        params.force = True
        result = UpdateByTagsCommand(self.config, 'tag,tag2', params).execute()
        assert not confirm_runned
        assert result[0]
