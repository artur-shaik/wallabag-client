# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.export_entry import ExportEntry
from wallabag.config import Configs


class TestExportEntry():

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

    @pytest.mark.parametrize('values', [('10', 'mobi'), (10, 'epub')])
    def test_api_url(self, values):
        api = ExportEntry(self.config, values[0], values[1])

        url = "url" + ApiMethod.GET_ENTRY.value.format(values[0])
        assert f'{url}/export.{values[1]}' == api._get_api_url()

    def test_api_url_none_format(self):
        api = ExportEntry(self.config, 10, '')

        with pytest.raises(ValueException):
            api._get_api_url()
