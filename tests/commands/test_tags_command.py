# -*- coding: utf-8 -*-

import pytest

from tags import tags_test
from wallabag.config import Configs
from wallabag.api.add_tag_to_entry import AddTagToEntry
from wallabag.api.api import Response
from wallabag.api.api import RequestException
from wallabag.api.get_tags import GetTags
from wallabag.api.get_tags_for_entry import GetTagsForEntry
from wallabag.commands.tags import TagsCommand, TagsCommandParams, TagsSubcommand


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

    def test_add_tags_to_entry(self, monkeypatch):
        tag_to_entry_runned = False

        def request(self):
            nonlocal tag_to_entry_runned
            tag_to_entry_runned = True
            return Response(200, """[]""")

        monkeypatch.setattr(AddTagToEntry, 'request', request)

        params = TagsCommandParams(entry_id=10, tags='tag1')
        params.command = TagsSubcommand.ADD
        result, msg = TagsCommand(self.config, params).run()
        assert tag_to_entry_runned
        assert result
        assert msg == 'Tags successfully added'

    @pytest.mark.parametrize('tags', tags_test)
    def test_tags_param(self, monkeypatch, tags):
        make_request_runned = False

        def request(self):
            nonlocal make_request_runned
            make_request_runned = True
            return Response(200, """[]""")

        monkeypatch.setattr(AddTagToEntry, 'request', request)

        params = TagsCommandParams(entry_id=10, tags=tags[0])
        params.command = TagsSubcommand.ADD
        result = TagsCommand(self.config, params).run()
        if tags[0]:
            assert make_request_runned
            assert result[0]
            assert result[1] == "Tags successfully added"
        else:
            assert not make_request_runned
            assert not result[0]
            assert result[1] == "tags value is empty"

    def test_tags_to_entry_empty_id(self):
        params = TagsCommandParams(tags='tags')
        params.command = TagsSubcommand.ADD
        result = TagsCommand(self.config, params).run()
        assert not result[0]
        assert result[1] == 'Entry id not specified'
