# -*- coding: utf-8 -*-

import click
from colorama import Back

from wallabag.api.api import Response
from wallabag.api.delete_entry import DeleteEntry
from wallabag.api.get_entry import GetEntry
from wallabag.commands.delete import DeleteCommand, DeleteCommandParams
from wallabag.config import Configs


class TestDeleteCommand():

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

    def test_not_confirmed_deletion(self, monkeypatch):
        def click_confirm(message):
            return False

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(click, 'confirm', click_confirm)

        params = DeleteCommandParams(1)
        result, output = DeleteCommand(self.config, params).execute()
        assert result
        assert output == 'Cancelling'

    def test_confirm_message(self, monkeypatch):
        confirm_runned = False

        def click_confirm(message):
            nonlocal confirm_runned
            confirm_runned = True
            assert message == (
                    f"{Back.RED}{DeleteCommand.WARN_MSG}:{Back.RESET}\n\n"
                    f"\ttitle\n\n"
                    f"Continue?")
            return False

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(click, 'confirm', click_confirm)

        params = DeleteCommandParams(1)
        result, output = DeleteCommand(self.config, params).execute()

        assert confirm_runned

    def test_deleted_successfully(self, monkeypatch):
        def click_confirm(message):
            return True

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        def request_delete(self):
            return Response(200, None)

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(DeleteEntry, 'request', request_delete)
        monkeypatch.setattr(click, 'confirm', click_confirm)

        params = DeleteCommandParams(1)
        result, output = DeleteCommand(self.config, params).execute()
        assert result
        assert output == 'Entry successfully deleted.'
