# -*- coding: utf-8 -*-

import pytest

from colorama import Fore, Back

from click.testing import CliRunner
from wallabag.api.api import Response, RequestException
from wallabag.api.get_entry import GetEntry
from wallabag.commands.show import (
        ShowCommand, ShowCommandParams, Alignment)
from wallabag.config import Configs
from wallabag.format_type import ScreenType
from wallabag import wallabag


def config__is_valid(self):
    return True


class TestShowCommand():

    runner = CliRunner()

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
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == f'title\n{"="*ShowCommand.FAILWIDTH}\ncontent'

    def test_entry_html_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, type=ScreenType.HTML)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                '<h1>title</h1>\n'
                'content')

    def test_entry_markdown(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h2>Sub title</h2><p>content<p>",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, type=ScreenType.MARKDOWN)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                '# title\n'
                '## Sub title\n\n'
                'content\n')

    def test_entry_html_strip_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, colors=False)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\n'
                'head\ncontent')

    def test_entry_html_strip_content_with_colors(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, colors=True)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\n'
                f'{Fore.BLUE}head{Fore.RESET}\ncontent')

    def test_entry_html_image_content(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content":\
                            "<h1>head</h1>content<img alt=\\"Message desc\\"\
                            src=\\"https://imag.es/1.jpg\\" />",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1, colors=False)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\n'
                'head\ncontent [IMAGE "Message desc"]')

    def test_entry_html_image_content_with_links(self, monkeypatch):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content":\
                            "<h1>head</h1>content<img alt=\\"Message desc\\"\
                            src=\\"https://imag.es/1.jpg\\" />",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(
                1, colors=False, image_links=True)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\nhead\ncontent '
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
                1, colors=True, image_links=True)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
            f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\n'
            f'{Fore.BLUE}he{Back.CYAN}ad{Back.RESET} [1]er text'
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
                1, colors=True, image_links=True)
        params.width = '100%'
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'title\n{"="*ShowCommand.FAILWIDTH}\n\n\n'
                f'{Fore.BLUE}he{Back.CYAN}ader text'
                f'{Fore.RESET}\ncontent\n\nend {Back.RESET} [1]anno')

    @pytest.mark.parametrize('values', [
        ('50%', " "*25, "="*int(ShowCommand.FAILWIDTH/2)),
        ('200', "", "="*ShowCommand.FAILWIDTH),
        ('70', " "*15, "="*70)])
    def test_custom_width(self, monkeypatch, values):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1)
        params.width = values[0]
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'{values[1]}title\n{values[1]}'
                f'{values[2]}\n{values[1]}content')

    @pytest.mark.parametrize('values', [
        ('80%', Alignment.CENTER,
            (ShowCommand.FAILWIDTH - ShowCommand.FAILWIDTH * 80 / 100) / 2,
            (ShowCommand.FAILWIDTH * 80 / 100)),
        ('80%', Alignment.RIGHT,
            (ShowCommand.FAILWIDTH - ShowCommand.FAILWIDTH * 80 / 100),
            (ShowCommand.FAILWIDTH * 80 / 100)),
        ('80%', Alignment.LEFT, 0, (ShowCommand.FAILWIDTH * 80 / 100))])
    def test_alignment(self, monkeypatch, values):
        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)

        params = ShowCommandParams(1)
        params.width = values[0]
        params.align = values[1]
        result, output = ShowCommand(self.config, params).execute()
        assert result
        assert output == (
                f'{" "*int(values[2])}title\n'
                f'{" "*int(values[2])}{"="*int(values[3])}\n'
                f'{" "*int(values[2])}content')

    def test_command_show(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'ShowCommand'
            assert command.params.entry_id == '1'
            assert command.params.align == Alignment.LEFT
            assert command.params.raw

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['show', '-r', '-a', 'left', '1'],
                catch_exceptions=False)
        assert result.exit_code == 0
        assert command_runned
