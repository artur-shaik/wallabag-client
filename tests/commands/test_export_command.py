# -*- coding: utf-8 -*-

import pytest
from datetime import datetime
from pathlib import PurePath, Path

from wallabag.config import Configs
from wallabag.commands.export import (
        ExportCommand, ExportCommandParams, FormatType)
from wallabag.api.api import Response
from wallabag.api.export_entry import ExportEntry


class TestExport():

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

        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get(
                        'epub'), PurePath(f'{tmp_path}/file'))).execute()
        assert result
        assert msg == f'Exported to: {tmp_path}/file'

    def test_empty_output(self, monkeypatch):

        def export_entry(self):
            return Response(
                    200, None, b'123', 'application/epub')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)

        result, msg = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub'))).execute()
        assert result
        assert msg == f'Exported to: {Path.cwd()}/{datetime.now().ctime()}'

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
        assert msg == f'Exported to: {Path.cwd()}/file.epub'

    def test_wrong_format_type(self, monkeypatch):

        def export_entry(self):
            return Response(200, None, b'123', 'application/epub')

        monkeypatch.setattr(ExportEntry, 'request', export_entry)

        command = ExportCommand(
                self.config, ExportCommandParams(
                    10, FormatType.get('epub2')))
        result, msg = command.execute()

        assert result
        assert command.params.format == FormatType.get('json')

    def test_format_not_specified(self):
        result, msg = ExportCommand(
                self.config, ExportCommandParams(10, None)).execute()

        assert not result
        assert msg == 'Format type not specified'

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
