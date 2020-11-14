# -*- coding: utf-8 -*-

from webbrowser import BaseBrowser

from click.testing import CliRunner
from wallabag.commands.open import OpenCommand, OpenCommandParams
from wallabag.config import Configs
from wallabag.api.get_entry import GetEntry
from wallabag.api.api import Response
from wallabag import wallabag


def config__is_valid(self):
    return True


class TestOpenCommand():

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

        result, msg = OpenCommand(
                self.config, OpenCommandParams(
                    1, browser='w3m')).execute()
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
                self.config, OpenCommandParams(
                    1, True, browser='w3m')).execute()
        assert open_new_tab_runned
        assert result
        assert not msg

    def test_command_open_simple(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert not command.params.open_original

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['open', '1', '-b', 'w3m'],
                catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0

    def test_command_open_original(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert command.params.open_original

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['open', '1', '-o', '-b', 'w3m'],
                catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0

    def test_command_browser(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'OpenCommand'
            assert command.params.entry_id == '1'
            assert command.params.browser == 'w3m'

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['open', '1', '-b', 'w3m'],
                catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0
