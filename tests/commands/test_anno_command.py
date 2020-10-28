# -*- coding: utf-8 -*-

import delorean
import humanize

from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.get_entry import GetEntry
from wallabag.commands.anno import AnnoCommand, AnnoCommandParams


class TestAnno():

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

    def test_list_entry_annotations(self, monkeypatch):

        def getentry_request(self):
            return Response(
                    200, (
                        '{"id": 1, "title": "title",'
                        '"content": "<h1>head</h1>content", "url": "url",'
                        '"is_archived": 0, "is_starred": 1,'
                        '"annotations": [{'
                        '"user": "User", "annotator_schema_version":'
                        ' "v1.0", "id": 1, "text": "content", '
                        '"created_at": "2020-10-28T10:50:51+0000", '
                        '"updated_at": "2020-10-28T10:50:51+0000", '
                        '"quote": "quote", "ranges": '
                        '[{"start": "/div[1]/p[1]", "startOffset": "23", '
                        '"end": "/div[1]/p[1]", "endOffset": "49"}]}]}'))

        monkeypatch.setattr(GetEntry, 'request', getentry_request)

        params = AnnoCommandParams()
        params.entry_id = 1
        result = AnnoCommand(self.config, params).execute()
        assert result[0]
        past = delorean.utcnow() - delorean.parse('2020-10-28T10:50:51+0000')
        assert result[1] == f'1. quote ({humanize.naturaltime(past)}) [7]'
