# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.delete_entry import DeleteEntry
from wallabag.config import Configs


class TestDeleteEntry():

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
        api = DeleteEntry(self.config, entry_id)

        url = "url" + ApiMethod.DELETE_ENTRY.value.format(entry_id)
        assert url == api._get_api_url()

    @pytest.mark.parametrize('entry_id', ["-10", -10, None, "none"])
    def test_api_url_wrong_arg(self, entry_id):
        api = DeleteEntry(self.config, entry_id)

        with pytest.raises(ValueException):
            api._get_api_url()
