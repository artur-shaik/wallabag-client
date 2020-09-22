# -*- coding: utf-8 -*-

from wallabag.api.api import Response
from wallabag.api.add_entry import AddEntry
from wallabag.api.entry_exists import EntryExists
from wallabag.commands.add import AddCommand, AddCommandParams
from wallabag.config import Configs


class TestAddCommand():

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

    def test_entry_existed_url(self, monkeypatch):
        make_request_runned = False
        url = "http://test/url"

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            assert request.api_params[EntryExists.ApiParams.URL.value] == url
            return Response(200, '{"exists": 1}')

        monkeypatch.setattr(EntryExists, '_make_request', _make_request)

        result = AddCommand(self.config, AddCommandParams(url)).run()
        assert make_request_runned
        assert result[0]
        assert result[1] == "The url was already saved."

    def test_add_existed_url(self, monkeypatch):

        def entry_exists(self):
            return Response(200, '{"exists": 1}')

        monkeypatch.setattr(EntryExists, 'request', entry_exists)

        params = AddCommandParams('url')
        result = AddCommand(self.config, params).run()
        assert result[0]
        assert result[1] == "The url was already saved."

    def test_add_command_params(self, monkeypatch):
        make_request_runned = False
        url = "http://test/url"
        title = 'test title'
        starred = True
        read = False

        def entry_not_exists(self):
            return Response(200, '{"exists": 0}')

        def _validate_url(self, url):
            return url

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            assert request.data[AddEntry.ApiParams.URL.value] == url
            assert request.data[AddEntry.ApiParams.ARCHIVE.value] == 0
            assert request.data[AddEntry.ApiParams.STARRED.value] == 1
            assert request.data[AddEntry.ApiParams.TITLE.value] == title
            return Response(200, None)

        monkeypatch.setattr(EntryExists, 'request', entry_not_exists)
        monkeypatch.setattr(AddEntry, '_make_request', _make_request)
        monkeypatch.setattr(AddEntry, '_validate_url', _validate_url)

        params = AddCommandParams(url, title, read=read, starred=starred)
        result = AddCommand(self.config, params).run()
        assert make_request_runned
        assert result[0]
        assert result[1] == "Entry successfully added."
