# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.add_entry import AddEntry, Params
from wallabag.config import Configs


def _is_valid_url(self, url):
    return True


class TestAddEntry():

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

    @pytest.mark.parametrize('entry_id', [10, "10"])
    def test_api_url(self, entry_id):
        api = AddEntry(self.config, "url", {})

        url = "url" + ApiMethod.ADD_ENTRY.value
        assert url == api._get_api_url()

    @pytest.mark.parametrize('values', [
        (Params.TITLE, "custom title",
            AddEntry.ApiParams.TITLE, "custom title"),
        (Params.READ, True, AddEntry.ApiParams.ARCHIVE, 1),
        (Params.READ, False, AddEntry.ApiParams.ARCHIVE, 0),
        (Params.STARRED, True, AddEntry.ApiParams.STARRED, 1),
        (Params.STARRED, False, AddEntry.ApiParams.STARRED, 0),
        ])
    def test_params(self, monkeypatch, values):
        monkeypatch.setattr(AddEntry, '_is_valid_url', _is_valid_url)

        api = AddEntry(self.config, "url", {
            values[0]: values[1]
        })

        data = api._get_data()
        assert data[values[2].value] == values[3]

    def test_empty_params(self, monkeypatch):
        monkeypatch.setattr(AddEntry, '_is_valid_url', _is_valid_url)

        api = AddEntry(self.config, "", {
            Params.TITLE: "",
            Params.STARRED: None
        })

        with pytest.raises(ValueException):
            api._get_data()

    def test_mixed_params(self, monkeypatch):
        monkeypatch.setattr(AddEntry, '_is_valid_url', _is_valid_url)

        api = AddEntry(self.config, "url", {
            Params.TITLE: "",
            Params.READ: True
        })

        data = api._get_data()
        assert AddEntry.ApiParams.TITLE.value not in data
        assert data[AddEntry.ApiParams.ARCHIVE.value] == 1
        assert 'https://url' == data[AddEntry.ApiParams.URL.value]

    def test_add_with_tags(self, monkeypatch):
        monkeypatch.setattr(AddEntry, '_is_valid_url', _is_valid_url)

        api = AddEntry(self.config, "url", {
            Params.TAGS: "tag1,tag2"
        })

        data = api._get_data()
        assert AddEntry.ApiParams.TAGS.value in data
