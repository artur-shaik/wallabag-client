# -*- coding: utf-8 -*-

import click

from colorama import Back

from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.delete_entry import DeleteEntry
from wallabag.api.get_list_entries import GetListEntries
from wallabag.commands.delete_by_tags import DeleteByTags, DeleteByTagsParams


class TestDeleteByTags():

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

    def test_remove_entries(self, monkeypatch):
        confirm_runned = False

        def success(self):
            return Response(200, None)

        def getlist_request(self):
            return Response(
                    200, (
                        '{"_embedded": {"items": [{"id": 1, "title": "title",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag","slug":"tag"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]},'
                        '{"id": 2, "title": "title 2",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"tags": ['
                        '{"id":7,"label":"tag","slug":"tag"},'
                        '{"id":13,"label":"tag2","slug":"tag2"}]}]}}'))

        def confirm(msg):
            nonlocal confirm_runned
            confirm_runned = True
            assert msg == (
                    f'{Back.RED}You are going to remove '
                    f'followed entries:{Back.RESET}'
                    f'\n\n\ttitle\n\ttitle 2\n\nContinue?')
            return True

        monkeypatch.setattr(GetListEntries, 'request', getlist_request)
        monkeypatch.setattr(DeleteEntry, 'request', success)
        monkeypatch.setattr(click, 'confirm', confirm)

        params = DeleteByTagsParams(tags='tag,tag2')
        result = DeleteByTags(self.config, params).execute()
        assert confirm_runned
        assert result[0]
