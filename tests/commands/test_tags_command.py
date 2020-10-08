# -*- coding: utf-8 -*-

from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.api import RequestException
from wallabag.api.get_tags import GetTags
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.tags import TagsCommand, TagsCommandParams


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

    def test_list_entry_tags(self, monkeypatch):
        def request(self):
            return Response(200, """[
            {"id": 3, "label": "book", "slug": "book"},
            {"id": 8, "label": "gut", "slug": "gut"},
            {"id": 7, "label": "security", "slug": "security"}]
            """)

        monkeypatch.setattr(GetTagsForEntry, 'request', request)

        params = TagsCommandParams(entry_id=10)
        result, msg = TagsCommand(self.config, params).run()
        assert result
        assert msg == '3. book\n7. security\n8. gut'

    def test_entry_not_found(self, monkeypatch):

        def request(self):
            response = Response(404, None)
            raise RequestException(
                    response.error_text, response.error_description)

        monkeypatch.setattr(GetTagsForEntry, 'request', request)

        params = TagsCommandParams(entry_id=10)
        result, msg = TagsCommand(self.config, params).run()
        assert not result
