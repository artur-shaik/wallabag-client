# -*- coding: utf-8 -*-

from wallabag.config import Configs
from wallabag.api.get_tags import GetTags
from wallabag.api.api import Response
from wallabag.commands.tags import TagsCommand


class TestTags():

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

    def test_list_tags(self, monkeypatch):

        def request(self):
            return Response(200, """[
            {"id": 3, "label": "book", "slug": "book"},
            {"id": 8, "label": "gut", "slug": "gut"},
            {"id": 7, "label": "security", "slug": "security"}]
            """)

        monkeypatch.setattr(GetTags, 'request', request)

        result, msg = TagsCommand(self.config).run()
        assert result
        assert msg == '3. book\n7. security\n8. gut'

    def test_empty_tag_list(self, monkeypatch):

        def request(self):
            return Response(200, """[]""")

        monkeypatch.setattr(GetTags, 'request', request)

        result, msg = TagsCommand(self.config).run()
        assert result
        assert not msg
