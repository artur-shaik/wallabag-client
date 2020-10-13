import os
import tempfile
import pathlib

import pytest

from wallabag.config import Configs, Options, Sections

from xdg.BaseDirectory import xdg_config_home as XDG_CONFIG_HOME


class TestConfigs():

    configs = None

    def teardown_method(self, method):
        os.close(self.fd)
        os.remove(self.path)

    def setup_method(self, method):
        self.fd, self.path = tempfile.mkstemp()
        with open(self.path, 'w') as f:
            f.write('')
        self.configs = Configs(self.path)
        if method.__name__ in ['test_get_config', 'test_is_token_expired',
                               'test_set_config', 'test_set_config_new']:
            self.configs.config.read_string("""
                    [api]
                    serverurl = https://server
                    [token]
                    expires = 1000
                    """)
        elif method.__name__ == 'test_is_valid__true':
            self.configs.config.read_string("""
                    [api]
                    serverurl = url
                    username = user
                    password = pass
                    [oauth2]
                    client = 100
                    secret = 100
                    """)
        elif method.__name__ == 'test_get_path':
            self.configs = Configs()

    def test_get_path(self):
        xdg_config = os.path.expanduser(XDG_CONFIG_HOME)
        expected = f"{xdg_config}/wallabag-cli/config.ini"

        actual = self.configs.get_path()
        assert expected == str(actual)

    def test_get_path_custom(self):
        expected = pathlib.PurePath("custom/directory")

        assert expected == self.configs.get_path(expected)

    @pytest.mark.parametrize(
            'condition',
            [(Sections.TOKEN, Options.EXPIRES, '1000', 'get'),
             (Sections.TOKEN, Options.ACCESS_TOKEN, None, 'get'),
             (Sections.API, Options.SERVERURL, "https://server", 'get'),
             (Sections.API, '', 0, 'getint'),
             (Sections.API, '', None, 'get'),
             ('', '', None, 'get'),
             (None, None, None, 'get'),
             (None, None, 0, 'getint'),
             (Sections.TOKEN, Options.EXPIRES, 1000, 'getint')])
    def test_get_config(self, condition):
        if condition[3] == 'get':
            assert self.configs.get(condition[0], condition[1]) == condition[2]
        elif condition[3] == 'getint':
            assert self.configs.getint(
                    condition[0], condition[1]) == condition[2]

    def test_is_token_expired(self):
        assert self.configs.is_token_expired()

    def test_is_token_expired_no_value(self):
        assert self.configs.is_token_expired()

    def test_is_valid__false(self):
        assert not self.configs.is_valid()

    def test_is_valid__true(self):
        assert self.configs.is_valid()

    def test_set_config(self):
        self.configs.set(Sections.TOKEN, Options.EXPIRES, str(500))
        assert self.configs.getint(Sections.TOKEN, Options.EXPIRES) == 500

    def test_set_config_new(self):
        self.configs.set(Sections.TOKEN, Options.ACCESS_TOKEN, 'abba')
        assert self.configs.get(Sections.TOKEN, Options.ACCESS_TOKEN) == 'abba'

    def test_load_or_create(self, monkeypatch):
        self.save_called = False

        def exists(path):
            return False

        def savemock(configs, path):
            self.save_called = True
            return True

        monkeypatch.setattr(os.path, 'exists', exists)
        monkeypatch.setattr(Configs, 'save', savemock)
        self.configs.load_or_create()
        assert self.save_called

    def test_load_or_create_load(self, monkeypatch):
        self.load_called = False

        def exists(path):
            return True

        def loadmock(configs, path):
            self.load_called = True
            return True

        monkeypatch.setattr(os.path, 'exists', exists)
        monkeypatch.setattr(Configs, 'load', loadmock)
        self.configs.load_or_create()
        assert self.load_called

    def test_load_or_create_value_error(self, monkeypatch):
        def exists(path):
            return False

        def savemock(configs, path):
            return False

        monkeypatch.setattr(os.path, 'exists', exists)
        monkeypatch.setattr(Configs, 'save', savemock)
        with pytest.raises(ValueError, match=Configs.LOAD_ERROR):
            self.configs.load_or_create()

    @pytest.mark.parametrize(
            'password',
            ['123456', 'password', 'secret'])
    def test_encryption(self, password):
        self.configs.set(Sections.API, Options.PASSWORD, password)
        encrypted = self.configs.config.get(Sections.API, Options.PASSWORD)
        plain = self.configs.get(Sections.API, Options.PASSWORD)

        assert encrypted != password
        assert plain == password
