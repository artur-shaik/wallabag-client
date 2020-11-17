# -*- coding: utf-8 -*-

import pytest
from colorama import Fore
from tabulate import tabulate

from click.testing import CliRunner
from wallabag.api.api import Api, Response
from wallabag.api.get_list_entries import GetListEntries
from wallabag.commands.list import ListCommand, ListParams
from wallabag.config import Configs
from wallabag import wallabag
from tags import tags_test


def get_authorization_header(self):
    return {'Authorization': "Bearer a1b2"}


def config__is_valid(self):
    return True


class TestListCommand():

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

    def test_empty_list(self, monkeypatch):

        def list_entries(self):
            text = '{ "_embedded": { "items": [] } }'
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert not entries

    @pytest.mark.parametrize('values', [
        ((0, 0), [1, '', 'title']), ((0, 1), [1, '', 'title']),
        ((1, 0), [1, '', 'title']), ((1, 1), [1, '', 'title']),
        ])
    def test_entries_list(self, monkeypatch, values):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                {
                "id": 1,
                "title": "title",
                "content": "content",
                "url": "url",
                "is_archived": %s,
                "is_starred": %s
                }
            ] } }
            ''' % (values[0][0], values[0][1])
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert entries
        assert entries == tabulate([values[1]])

    def test_list(self, monkeypatch):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                { "id": 1, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1},
                { "id": 2, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1}
            ] } }
            '''
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert len(entries.split('\n')) == 4

    @pytest.mark.parametrize('tags', tags_test)
    def test_tags_param(self, monkeypatch, tags):
        make_request_runned = False

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            assert GetListEntries.ApiParams.TAGS.value in request.api_params
            assert request.api_params[
                    GetListEntries.ApiParams.TAGS.value].split(',') == tags[1]
            text = '{ "_embedded": { "items": [] } }'
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, '_make_request', _make_request)
        monkeypatch.setattr(
                Api, '_get_authorization_header', get_authorization_header)

        command = ListCommand(self.config, ListParams(tags=tags[0]))
        result, entries = command.execute()
        if tags[0]:
            assert make_request_runned
            assert result
        else:
            assert not make_request_runned
            assert not result

    def test_annotated_entry(self, monkeypatch):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                { "id": 2, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1,
                "annotations": [{
                    "user": "User", "annotator_schema_version":
                    "v1.0", "id": 1, "text": "content",
                    "created_at": "2020-10-28T10:50:51+0000",
                    "updated_at": "2020-10-28T10:50:51+0000",
                    "quote": "quote", "ranges":
                    [{"start": "/div[1]/p[1]", "startOffset": "23",
                    "end": "/div[1]/p[1]", "endOffset": "49"}]}]},
                { "id": 1, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1}]}}
            '''
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert entries == tabulate(
                [
                    [2, '', f'title {Fore.BLUE}{Fore.RESET}'],
                    [1, '', 'title']])

    def test_tagged_entry(self, monkeypatch):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                { "id": 2, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1},
                { "id": 1, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1,
                "tags": [
                        {"id":7,"label":"tag","slug":"tag"},
                        {"id":13,"label":"tag2","slug":"tag2"}]}
                ]}}
            '''
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert entries == tabulate(
                [
                    [2, '', 'title'],
                    [1, '', f'title {Fore.BLUE}{Fore.RESET}']])

    def test_tagged_and_annotated_entry(self, monkeypatch):

        def list_entries(self):
            text = '''
            { "_embedded": { "items": [
                { "id": 2, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1},
                { "id": 1, "title": "title", "content": "content",
                "url": "url", "is_archived": 0, "is_starred": 1,
                "annotations": [{
                    "user": "User", "annotator_schema_version":
                    "v1.0", "id": 1, "text": "content",
                    "created_at": "2020-10-28T10:50:51+0000",
                    "updated_at": "2020-10-28T10:50:51+0000",
                    "quote": "quote", "ranges":
                    [{"start": "/div[1]/p[1]", "startOffset": "23",
                    "end": "/div[1]/p[1]", "endOffset": "49"}]}],
                "tags": [
                        {"id":7,"label":"tag","slug":"tag"},
                        {"id":13,"label":"tag2","slug":"tag2"}]}
                ]}}
            '''
            return Response(200, text)

        monkeypatch.setattr(GetListEntries, 'request', list_entries)

        command = ListCommand(self.config)
        result, entries = command.execute()
        assert result
        assert entries == tabulate(
                [
                    [2, '', 'title'],
                    [1, '', (
                        f'title {Fore.BLUE}{Fore.RESET} '
                        f'{Fore.BLUE}{Fore.RESET}')]])

    @pytest.mark.parametrize(
            'command_class', [
                (['list'], 'ListCommand'),
                (['list', '-c'], 'CountCommand')])
    def test_list_command(self, monkeypatch, command_class):
        command_runned = False

        def run_command(command, quite=False):
            nonlocal command_runned
            command_runned = True
            assert command.__class__.__name__ == command_class[1]

        monkeypatch.setattr(wallabag, 'run_command', run_command)
        monkeypatch.setattr(Configs, 'is_valid', config__is_valid)

        result = self.runner.invoke(
                wallabag.cli, command_class[0], catch_exceptions=False)
        assert command_runned
        assert result.exit_code == 0
