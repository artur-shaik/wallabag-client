# -*- coding: utf-8 -*-

from colorama import Fore, Back

from wallabag.api.api import Response, RequestException
from wallabag.api.get_entry import GetEntry
from wallabag.commands.show import ShowCommand, ShowCommandParams
from wallabag.config import Configs


class TestShowCommand():

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

    def test_entry_not_exist(self, monkeypatch):
        def request(self):
            response = Response(404, None)
            raise RequestException(
                    response.error_text, response.error_description)
        monkeypatch.setattr(GetEntry, 'request', request)

        result, output = ShowCommand(
                self.config, ShowCommandParams(1000)).execute()
        assert not result
        assert output == "Error: 404: API was not found."

    def test_entry_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == 'title\n\n\ncontent'

    def test_entry_html_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, html=True)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == 'title\n\n\n<h1>head</h1>content'

    def test_entry_html_strip_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, html=False, colors=False)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == 'title\n\n\n\n\nhead\ncontent'

    def test_entry_html_strip_content_with_colors(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, html=False, colors=True)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == f'title\n\n\n\n\n{Fore.BLUE}head{Fore.RESET}\ncontent'

    def test_entry_html_image_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content":\
                            "<h1>head</h1>content<img alt=\\"Message desc\\"\
                            src=\\"https://imag.es/1.jpg\\" />",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, html=False, colors=False)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == 'title\n\n\n\n\nhead\ncontent [IMAGE "Message desc"]'

    def test_entry_html_image_content_with_links(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content":\
                            "<h1>head</h1>content<img alt=\\"Message desc\\"\
                            src=\\"https://imag.es/1.jpg\\" />",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(
                1, html=False, colors=False, image_links=True)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                'title\n\n\n\n\nhead\ncontent '
                '[IMAGE "Message desc" (https://imag.es/1.jpg)]')

    def test_entry_html_image_content_with_annotations(self, monkeypatch):
        def request(self):
            return Response(
                    200, (
                        '{"id": 1, "title": "title", "content":'
                        '"<h1>header text</h1>content<img alt=\\"Message\\"'
                        'src=\\"https://imag.es/1.jpg\\" />",'
                        '"url": "url", "is_archived": 0, "is_starred": 1,'
                        '"annotations":[{'
                        '"user": "User", "annotator_schema_version":'
                        ' "v1.0", "id": 1, "text": "content", '
                        '"created_at": "2020-10-28T10:50:51+0000", '
                        '"updated_at": "2020-10-28T10:50:51+0000", '
                        '"quote": "quote", "ranges": '
                        '[{"start": "/h1", "startOffset": "2", '
                        '"end": "/h1", "endOffset": "4"}]}]}'))

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(
                1, html=False, colors=True, image_links=True)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
            f'title\n\n\n\n\n{Fore.BLUE}he{Back.CYAN}ad{Back.RESET} [1]er text'
            f'{Fore.RESET}\ncontent '
            '[IMAGE "Message" (https://imag.es/1.jpg)]')

    def test_entry_html_content_with_annotations_multiline(
            self, monkeypatch):
        def request(self):
            return Response(
                200, ('{"id": 1, "title": "title", "content":'
                      '"<h1>header text</h1>content<p>end anno</p>",'
                      '"url": "url", "is_archived": 0, "is_starred": 1,'
                      '"annotations":[{'
                      '"user": "User", "annotator_schema_version":'
                      ' "v1.0", "id": 1, "text": "content", '
                      '"created_at": "2020-10-28T10:50:51+0000", '
                      '"updated_at": "2020-10-28T10:50:51+0000", '
                      '"quote": "quote", "ranges": '
                      '[{"start": "/h1", "startOffset": "2", '
                      '"end": "/p", "endOffset": "4"}]}]}'))

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(
                1, html=False, colors=True, image_links=True)
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n\n\n\n\n{Fore.BLUE}he{Back.CYAN}ader text'
                f'{Fore.RESET}\ncontent\n\nend {Back.RESET} [1]anno')
