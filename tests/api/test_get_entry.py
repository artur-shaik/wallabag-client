# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.get_entry import GetEntry
from wallabag.config import Configs


class TestGetEntry():

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

    @pytest.mark.parametrize('entry_id', ["10", 10])
    def test_api_url(self, entry_id):
        api = GetEntry(self.config, entry_id)

        url = "url" + ApiMethod.GET_ENTRY.value.format("10")
        assert url == api._get_api_url()

    @pytest.mark.parametrize('entry_id', ["-10", -10, None, "none"])
    def test_api_url_wrong_arg(self, entry_id):
        api = GetEntry(self.config, entry_id)

        with pytest.raises(ValueException):
            api._get_api_url()
