# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.update_entry import UpdateEntry, Params
from wallabag.config import Configs


class TestUpdateEntry():

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
        api = UpdateEntry(self.config, entry_id, {})

        url = "url" + ApiMethod.UPDATE_ENTRY.value.format(entry_id)
        assert url == api._get_api_url()

    @pytest.mark.parametrize('values', [
        (Params.TITLE, "new title", UpdateEntry.ApiParams.TITLE, "new title"),
        (Params.READ, True, UpdateEntry.ApiParams.ARCHIVE, 1),
        (Params.READ, False, UpdateEntry.ApiParams.ARCHIVE, 0),
        (Params.STAR, True, UpdateEntry.ApiParams.STARRED, 1),
        (Params.STAR, False, UpdateEntry.ApiParams.STARRED, 0),
        ])
    def test_params(self, values):
        api = UpdateEntry(self.config, "10", {
            values[0]: values[1]
        })

        data = api._get_data()
        assert data[values[2].value] == values[3]

    def test_empty_params(self):
        api = UpdateEntry(self.config, "10", {
            Params.TITLE: "",
            Params.STAR: None
        })

        with pytest.raises(ValueException):
            api._get_data()

    def test_mixed_params(self):
        api = UpdateEntry(self.config, "10", {
            Params.TITLE: "",
            Params.READ: True
        })

        data = api._get_data()
        assert UpdateEntry.ApiParams.TITLE.value not in data
        assert data[UpdateEntry.ApiParams.ARCHIVE.value] == 1
