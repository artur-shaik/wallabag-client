# -*- coding: utf-8 -*-

import os
import pytest
import re
from pathlib import PurePath, Path

from click.testing import CliRunner
from wallabag.config import Configs
from wallabag.commands.export import (
        ExportCommand, ExportCommandParams, FormatType)
from wallabag.api.api import Response
from wallabag.api.export_entry import ExportEntry
from wallabag.api.get_entry import GetEntry
from wallabag import wallabag


def config__is_valid(self):
    return True


class TestExport():

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

    def test_export(self, monkeypatch, tmp_path):

        def export_entry(self):
            return Response(200, None, b'123', 'application/epub')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)

        params = ExportCommandParams(
                    10, FormatType.get(
                        'epub'), PurePath(f'{tmp_path}/file.epub'))
        params.filename_with_id = False
        result, msg = ExportCommand(
                self.config, params).execute()
        assert result
        assert msg == f'Exported to: {tmp_path}/file.epub'

    def test_empty_output(self, monkeypatch, tmpdir):

        def export_entry(self):
            return Response(
                    200, None, b'123', 'application/epub')

        def get_entry(self):
            return Response(
                    200, '{"id": 10, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)
        monkeypatch.setattr(GetEntry, 'request', get_entry)

        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub'), PurePath(tmpdir))).execute()
        assert result
        assert f'Exported to: {PurePath(tmpdir)}/10. title.epub' == msg

    def test_non_existed_directory(self, monkeypatch, tmpdir):

        def export_entry(self):
            return Response(
                    200, None, b'123', 'application/epub')

        def get_entry(self):
            return Response(
                    200, '{"id": 10, "title": "title", "content": "content",\
                            "url": "url", "is_archived": 0, "is_starred": 1}')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)
        monkeypatch.setattr(GetEntry, 'request', get_entry)

        tmpdir = tmpdir + '/new_dir/'
        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub'), PurePath(tmpdir))).execute()
        assert result
        assert f'Exported to: {PurePath(tmpdir)}/10. title.epub' == msg

    def test_empty_output_cdisposition(self, monkeypatch):

        def export_entry(self):
            return Response(
                    200, None, b'123', 'application/epub',
                    'attachment; filename="file.epub"')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)

        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub'))).execute()
        assert result
        assert msg == f'Exported to: {Path.cwd()}/10. file.epub'

        os.remove(f'{Path.cwd()}/10. file.epub')

    def test_wrong_format_type(self, monkeypatch, tmpdir):
        command = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub2'), PurePath(tmpdir)))
        result, msg = command.execute()

        assert not result
        assert msg == 'Unsupported type'

    def test_format_not_specified(self):
        result, msg = ExportCommand(
                self.config, ExportCommandParams(10, None)).execute()

        assert not result
        assert msg == 'Type not specified'

    @pytest.mark.parametrize('values', [
        (None, 'Entry ID not specified'),
        (-10, 'Entry ID not specified'),
        ('-10', 'Entry ID not specified'),
        ('foo', 'Wrong Entry ID value')])
    def test_wrong_entry_id(self, values):
        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    values[0], FormatType.get('json'))).execute()

        assert not result
        assert msg == values[1]

    def test_command_export(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'ExportCommand'
            assert command.params.entry_id == '1'

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['export', '1'], catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0

    def test_command_export_format(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'ExportCommand'
            assert command.params.entry_id == '1'
            assert command.params.type.name == 'PDF'

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['export', '1', '-f', 'pdf'],
                catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0

    def test_command_export_output(self, monkeypatch):
        command_runned = False

        def run_command(command, quiet=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == 'ExportCommand'
            assert command.params.entry_id == '1'
            assert command.params.output_file == PurePath('/tmp')

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, ['export', '1', '-f', 'pdf', '-o', '/tmp'],
                catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0
