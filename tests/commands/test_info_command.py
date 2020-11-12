# -*- coding: utf-8 -*-

from colorama import Fore

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

        self.f_c = Fore.LIGHTBLUE_EX
        self.f_rst = Fore.RESET

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
                f'{self.f_c}ID{self.f_rst}: 1\n'
                f'{self.f_c}Title{self.f_rst}: title\n'
                f'{self.f_c}Url{self.f_rst}: url\n'
                f'{self.f_c}Tags{self.f_rst}: tag1 tag2\n'
                f'{self.f_c}Is read{self.f_rst}: False\n'
                f'{self.f_c}Is starred{self.f_rst}: True\n'
                f'{self.f_c}Created at{self.f_rst}: '
                'Apr 11, 2020, 11:37:45 AM\n'
                f'{self.f_c}Published by{self.f_rst}: Publisher Name\n'
                f'{self.f_c}Reading time{self.f_rst}: 9 min\n'
                f'{self.f_c}Preview picture{self.f_rst}: '
                'https://www.site.coms/pic.jpg')

    def test_info_with_anno(self, monkeypatch):

        def request(self):
            return Response(
                    200, (
                     '{"id": 1, "title": "title", "content": "content",'
                     '"url": "url", "is_archived": 0, "is_starred": 1, '
                     '"created_at": "2020-11-04T11:37:45+0000", '
                     '"updated_at": "2020-11-04T11:37:45+0000", '
                     '"starred_at": null, '
                     '"annotations": ['
                     '{"user": null, "annotator_schema _version": "v1.0", '
                     '"id": 3, "text": "Are you texting?", '
                     '"created_at": "2020-11-04T05:57:26+0000", '
                     '"updated_at": "2020-11-04T05:57:26+0000", '
                     '"quote": "Our current quote", '
                     '"ranges": ['
                     '{"start": "/p[5]", "startOffset": "0", "end": "/p[5]", '
                     '"endOffset": "19"}]},'
                     '{"user": null, "annotator_schema_version": "v1.0", '
                     '"id": 4, "text": "This is text", '
                     '"created_at": "2020-11-04T05:57:46+0000", '
                     '"updated_at": "2020-11-04T05:57:46+0000", '
                     '"quote": "Email Security", "ranges": ['
                     '{"start": "/h3[4]", "startOffset": "0", "end": "/h3[4]",'
                     '"endOffset": "14"}]}],'
                     '"mimetype": "text/html", "language": "ru_RU",'
                     '"reading_time": 9, "domain_name": "www.site.com"}'))

        monkeypatch.setattr(GetEntry, 'request', request)

        params = InfoCommandParams(entry_id=10)
        result, msg = InfoCommand(self.config, params).execute()
        assert result
        assert msg == (
                f'{self.f_c}ID{self.f_rst}: 1\n'
                f'{self.f_c}Title{self.f_rst}: title\n'
                f'{self.f_c}Url{self.f_rst}: url\n'
                f'{self.f_c}Annotations{self.f_rst}: 2\n'
                f'{self.f_c}Is read{self.f_rst}: False\n'
                f'{self.f_c}Is starred{self.f_rst}: True\n'
                f'{self.f_c}Created at{self.f_rst}: '
                'Apr 11, 2020, 11:37:45 AM\n'
                f'{self.f_c}Reading time{self.f_rst}: 9 min\n')

    def test_no_id(self):
        params = InfoCommandParams(None)
        result, msg = InfoCommand(self.config, params).execute()
        assert not result
        assert msg == 'Entry ID not specified'

        result, msg = InfoCommand(self.config, None).execute()
        assert not result
        assert msg == 'Entry ID not specified'
