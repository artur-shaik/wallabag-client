# -*- coding: utf-8 -*-

from webbrowser import BaseBrowser

from click.testing import CliRunner
from wallabag.commands.open import OpenCommand, OpenCommandParams
from wallabag.config import Configs
from wallabag.api.get_entry import GetEntry
from wallabag.api.api import Response
from wallabag import wallabag


class TestOpenCommand():

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

    def test_open_command(self, monkeypatch):
        open_new_tab_runned = False

        def open_new_tab(self, url):
            nonlocal open_new_tab_runned
            open_new_tab_runned = True
            assert url == 'url/view/1'

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(BaseBrowser, 'open_new_tab', open_new_tab)

        result, msg = OpenCommand(self.config, OpenCommandParams(1)).execute()
        assert open_new_tab_runned
        assert result
        assert not msg

    def test_open_original(self, monkeypatch):
        open_new_tab_runned = False

        def open_new_tab(self, url):
            nonlocal open_new_tab_runned
            open_new_tab_runned = True
            assert url == 'url'

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "<h1>head</h1>content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(BaseBrowser, 'open_new_tab', open_new_tab)

        result, msg = OpenCommand(
                self.config, OpenCommandParams(1, True)).execute()
        assert open_new_tab_runned
        assert result
        assert not msg

    def test_command_open_simple(self, monkeypatch):
        def run_command(command, quiet=False):
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert not command.params.open_original

        monkeypatch.setattr(wallabag, 'run_command', run_command)

        runner = CliRunner()
        result = runner.invoke(wallabag.cli, ['open', '1'])
        print(result.exception)
        assert result.exit_code == 0

    def test_command_open_original(self, monkeypatch):
        def run_command(command, quiet=False):
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert command.params.open_original

        monkeypatch.setattr(wallabag, 'run_command', run_command)

        runner = CliRunner()
        result = runner.invoke(wallabag.cli, ['open', '1', '-o'])
        print(result.exception)
        assert result.exit_code == 0

    def test_command_browser(self, monkeypatch):
        def run_command(command, quiet=False):
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert command.params.browser == 'elinks'

        monkeypatch.setattr(wallabag, 'run_command', run_command)

        runner = CliRunner()
        result = runner.invoke(wallabag.cli, ['open', '1', '-b', 'elinks'])
        print(result.exception)
        assert result.exit_code == 0
