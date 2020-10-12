# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.delete_tag_from_entry import DeleteTagFromEntry
from wallabag.config import Configs


class TestDeleteTagFromEntry():

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

    def test_api_url(self):
        entry_id = 1
        tag_id = '2'
        api = DeleteTagFromEntry(self.config, entry_id, tag_id)
        url = 'url' + ApiMethod.DELETE_TAG_FROM_ENTRY.value.format(
                entry_id, tag_id)
        assert url == api._get_api_url()

    @pytest.mark.parametrize('entry_id', ["-10", -10, None, "none"])
    def test_wrong_args(self, entry_id):
        api = DeleteTagFromEntry(self, entry_id, '10')
        with pytest.raises(ValueException):
            api._get_api_url()
