# -*- coding: utf-8 -*-

import pytest

from colorama import Fore

from tags import tags_test
from wallabag.api.add_entry import AddEntry
from wallabag.api.api import Api, Response
from wallabag.api.entry_exists import EntryExists
from wallabag.commands.add import AddCommand, AddCommandParams
from wallabag.config import Configs


def get_authorization_header(self):
    return {'Authorization': "Bearer a1b2"}


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
        monkeypatch.setattr(
                Api, '_get_authorization_header', get_authorization_header)

        result = AddCommand(self.config, AddCommandParams(url)).execute()
        assert make_request_runned
        assert result[0]
        assert result[1] == "The url was already saved."

    def test_add_existed_url(self, monkeypatch):

        def entry_exists(self):
            return Response(200, '{"exists": 1}')

        monkeypatch.setattr(EntryExists, 'request', entry_exists)

        params = AddCommandParams('url')
        result = AddCommand(self.config, params).execute()
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
            return Response(200, (
                    '{"is_archived":0,"is_starred":0,"user_name":"wallabag",'
                    '"user_email":"","user_id":1,"tags":[],"is_public":false,'
                    '"id":15,"uid":null,"title":"title of entry",'
                    '"url":"url","content":"content",'
                    '"created_at":"2020-11-11T05:02:11+0000",'
                    '"updated_at":"2020-11-11T05:02:11+0000",'
                    '"published_at":null,"published_by":null,'
                    '"starred_at":null,"annotations":null}'
                ))

        monkeypatch.setattr(EntryExists, 'request', entry_not_exists)
        monkeypatch.setattr(AddEntry, '_make_request', _make_request)
        monkeypatch.setattr(AddEntry, '_validate_url', _validate_url)
        monkeypatch.setattr(
                Api, '_get_authorization_header', get_authorization_header)

        params = AddCommandParams(url, title, read=read, starred=starred)
        result = AddCommand(self.config, params).execute()
        assert make_request_runned
        assert result[0]
        assert result[1] == (
                "Entry successfully added:\n\n"
                f"\t{Fore.GREEN}15. title of entry{Fore.RESET}\n")

    @pytest.mark.parametrize('tags', tags_test)
    def test_add_with_tags(self, monkeypatch, tags):
        make_request_runned = False
        url = "http://test/url"
        title = 'test title'

        def entry_not_exists(self):
            return Response(200, '{"exists": 0}')

        def _validate_url(self, url):
            return url

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            assert request.data[AddEntry.ApiParams.URL.value] == url
            assert request.data[
                    AddEntry.ApiParams.TAGS.value].split(',') == tags[1]
            assert request.data[AddEntry.ApiParams.TITLE.value] == title
            return Response(200, (
                    '{"is_archived":0,"is_starred":0,"user_name":"wallabag",'
                    '"user_email":"","user_id":1,"tags":[],"is_public":false,'
                    '"id":15,"uid":null,"title":"title of entry",'
                    '"url":"url","content":"content",'
                    '"created_at":"2020-11-11T05:02:11+0000",'
                    '"updated_at":"2020-11-11T05:02:11+0000",'
                    '"published_at":null,"published_by":null,'
                    '"starred_at":null,"annotations":null,'
                    '"mimetype":"text/html","language":null,'
                    '"reading_time":7,"domain_name":"domain",'
                    '"preview_picture":"http://pic.com/pic.png",'
                    '"http_status":"200","headers":null,"origin_url":null,'
                    '"_links":{"self":{"href":"/api/entries/15"}}}'
                ))

        monkeypatch.setattr(EntryExists, 'request', entry_not_exists)
        monkeypatch.setattr(AddEntry, '_make_request', _make_request)
        monkeypatch.setattr(AddEntry, '_validate_url', _validate_url)
        monkeypatch.setattr(
                Api, '_get_authorization_header', get_authorization_header)

        params = AddCommandParams(url, title, tags=tags[0])
        result = AddCommand(self.config, params).execute()
        if tags[0]:
            assert make_request_runned
            assert result[0]
            assert result[1] == (
                    "Entry successfully added:\n\n"
                    f"\t{Fore.GREEN}15. title of entry{Fore.RESET}\n")
        else:
            assert not make_request_runned
            assert not result[0]
            assert result[1] == "tags value is empty"
