# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import Response
from wallabag.api.get_list_entries import GetListEntries
from wallabag.commands.list import ListCommand, ListParams
from wallabag.config import Configs


class TestListCommand():

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

    def test_empty_list(self, monkeypatch):

        def list_entries(self):
            text = '{ "_embedded": { "items": [] } }'
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.run()
        assert result
        assert not entries

    @pytest.mark.parametrize('values', [
        ((0, 0), '1 title'), ((0, 1), '1 * title'),
        ((1, 0), '1 ✔ title'), ((1, 1), '1 ✔* title'),
        ])
    def test_entries_list(self, monkeypatch, values):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                {
                "id": 1,
                "title": "title",
                "content": "content",
                "url": "url",
                "is_archived": %s,
                "is_starred": %s
                }
            ] } }
            ''' % (values[0][0], values[0][1])
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.run()
        assert result
        assert entries
        assert entries == values[1]

    def test_list(self, monkeypatch):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                { "id": 1, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1},
                { "id": 2, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1}
            ] } }
            '''
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.run()
        assert result
        assert len(entries.split('\n')) == 2
