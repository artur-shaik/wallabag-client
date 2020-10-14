# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.add_tag_to_entry import AddTagToEntry, Params
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

    @pytest.mark.parametrize('entry_id', [10, "10", ''])
    def test_api_url(self, entry_id):
        api = AddTagToEntry(self.config, {Params.ENTRY_ID: entry_id})

        url = "url" + ApiMethod.ADD_TAGS_TO_ENTRY.value.format(entry_id)
        if not entry_id:
            with pytest.raises(ValueException):
                api._get_api_url()
        else:
            assert url == api._get_api_url()

    def test_params(self, monkeypatch):
        monkeypatch.setattr(AddTagToEntry, '_is_valid_url', _is_valid_url)

        api = AddTagToEntry(self.config, {
            Params.ENTRY_ID: 10,
            Params.TAGS: 'tag1,tag2'
        })

        data = api._get_data()
        assert AddTagToEntry.ApiParams.TAGS.value in data
