# -*- coding: utf-8 -*-

import delorean
import humanize

from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.get_entry import GetEntry
from wallabag.api.delete_annotation import DeleteAnnotation
from wallabag.commands.anno import (
        AnnoCommand, AnnoCommandParams, AnnoSubcommand)


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

    def test_remove_annotation(self, monkeypatch):

        def request_success(self):
            return Response(200, None)

        monkeypatch.setattr(DeleteAnnotation, 'request', request_success)

        params = AnnoCommandParams()
        params.anno_id = 1
        params.command = AnnoSubcommand.REMOVE
        result = AnnoCommand(self.config, params).execute()
        assert result[0]
        assert result[1] == 'Annotation successfully deleted'

    def test_show_annotations(self, monkeypatch):

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
                        '"end": "/div[1]/p[1]", "endOffset": "49"}]},{'
                        '"user": "User", "annotator_schema_version":'
                        ' "v1.0", "id": 2, "text": "another content", '
                        '"created_at": "2020-10-28T10:50:51+0000", '
                        '"updated_at": "2020-10-28T10:50:51+0000", '
                        '"quote": "another quote", "ranges": '
                        '[{"start": "/div[1]/p[2]", "startOffset": "23", '
                        '"end": "/div[1]/p[2]", "endOffset": "49"}]}]}'))

        monkeypatch.setattr(GetEntry, 'request', getentry_request)

        params = AnnoCommandParams()
        params.entry_id = 1
        params.command = AnnoSubcommand.SHOW
        result = AnnoCommand(self.config, params).execute()
        assert result[0]
        past = delorean.utcnow() - delorean.parse('2020-10-28T10:50:51+0000')
        assert result[1] == (
                f'1. quote ({humanize.naturaltime(past)}):\n\n\tcontent\n\n'
                f'2. another quote ({humanize.naturaltime(past)}):'
                '\n\n\tanother content\n')

    def test_show_annotations_by_id(self, monkeypatch):

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
                        '"end": "/div[1]/p[1]", "endOffset": "49"}]},{'
                        '"user": "User", "annotator_schema_version":'
                        ' "v1.0", "id": 2, "text": "another content", '
                        '"created_at": "2020-10-28T10:50:51+0000", '
                        '"updated_at": "2020-10-28T10:50:51+0000", '
                        '"quote": "another quote", "ranges": '
                        '[{"start": "/div[1]/p[2]", "startOffset": "23", '
                        '"end": "/div[1]/p[2]", "endOffset": "49"}]}]}'))

        monkeypatch.setattr(GetEntry, 'request', getentry_request)

        params = AnnoCommandParams()
        params.entry_id = 1
        params.anno_id = 2
        params.command = AnnoSubcommand.SHOW
        result = AnnoCommand(self.config, params).execute()
        assert result[0]
        past = delorean.utcnow() - delorean.parse('2020-10-28T10:50:51+0000')
        assert result[1] == (
                f'2. another quote ({humanize.naturaltime(past)}):'
                '\n\n\tanother content\n')

    def test_show_empty_params(self):
        params = AnnoCommandParams()
        params.command = AnnoSubcommand.SHOW
        result = AnnoCommand(self.config, params).execute()
        assert not result[0]
        assert result[1] == 'Entry ID not specified'

    def test_list_empty_params(self):
        params = AnnoCommandParams()
        params.command = AnnoSubcommand.LIST
        result = AnnoCommand(self.config, params).execute()
        assert not result[0]
        assert result[1] == 'Entry ID not specified'

    def test_remove_empty_params(self):
        params = AnnoCommandParams()
        params.command = AnnoSubcommand.REMOVE
        result = AnnoCommand(self.config, params).execute()
        assert not result[0]
        assert result[1] == 'Annotation ID not specified'
