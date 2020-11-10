# -*- coding: utf-8 -*-

from wallabag.commands.info import InfoCommand, InfoCommandParams
from wallabag.config import Configs
from wallabag.api.api import Response
from wallabag.api.get_entry import GetEntry


class TestInfoCommand():

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

    def test_info_success(self, monkeypatch):

        def request(self):
            return Response(
                    200, (
                     '{"id": 1, "title": "title", "content": "content",'
                     '"url": "url", "is_archived": 0, "is_starred": 1, '
                     '"tags": ['
                     '{"id": 0, "label": "tag1", "slug": "tag1"},'
                     '{"id": 1, "label": "tag2", "slug": "tag2"}],'
                     '"created_at": "2020-11-04T11:37:45+0000", '
                     '"updated_at": "2020-11-04T11:37:45+0000", '
                     '"published_at": null, "published_by":'
                     '["Publisher Name"],'
                     '"starred_at": null, "annotations": [], '
                     '"mimetype": "text/html", "language": "ru_RU",'
                     '"reading_time": 9, "domain_name": "www.site.com",'
                     '"preview_picture": "https://www.site.coms/pic.jpg"}'))

        monkeypatch.setattr(GetEntry, 'request', request)

        params = InfoCommandParams(entry_id=10)
        result, msg = InfoCommand(self.config, params).execute()
        assert result
        assert msg == (
                'ID: 1\n'
                'Title: title\n'
                'Url: url\n'
                'Tags: tag1 tag2\n'
                'Is read: False\n'
                'Is starred: True\n'
                'Created at: Apr 11, 2020, 11:37:45 AM\n'
                'Published by: Publisher Name\n'
                'Reading time: 9 min\n'
                'Preview picture: https://www.site.coms/pic.jpg')

    def test_no_id(self):
        params = InfoCommandParams(None)
        result, msg = InfoCommand(self.config, params).execute()
        assert not result
        assert msg == 'Entry ID not specified'

        result, msg = InfoCommand(self.config, None).execute()
        assert not result
        assert msg == 'Entry ID not specified'
