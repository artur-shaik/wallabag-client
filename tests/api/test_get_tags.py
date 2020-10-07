# -*- coding: utf-8 -*-

from wallabag.api.api import ApiMethod
from wallabag.api.get_tags import GetTags
from wallabag.config import Configs


class TestGetTags():

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
        api = GetTags(self.config)

        url = "url" + ApiMethod.GET_TAGS.value
        assert url == api._get_api_url()
