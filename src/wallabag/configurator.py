# -*- coding: utf-8 -*-

import re
from abc import ABC, abstractmethod

import click

from wallabag.api import Api, Error
from wallabag.config import Options, Sections


class Configurator():

    def __init__(self, config):
        self.config = config

    def start(self, options=[]):
        if not options:
            options = ConfigOption.get_all(self.config)
        for option in options:
            while not option.setup(self.config):
                pass

        self.config.save()


class Validator():

    def __init__(self, config):
        self.config = config
        self.api = Api(config)
        self.response = {
            'invalid_grant': (
                False, None, [UsernameOption(), PasswordOption()]),
            'invalid_client': (
                False, None, [ClientOption(), SecretOption()])
        }

    def check_oauth(self):
        response = self.api.api_token()
        if response.has_error():
            if response.error == Error.http_bad_request:
                click.echo(response.error_description)
                return self.response[response.error_text]
            return (False, response.error_description, None)
        return (True, "The configuration is ok.", None)

    def check(self):
        if not self.config.is_valid():
            return (False, "The config is missing or incomplete.")

        response = self.api.api_version()
        if response.has_error():
            return (False, "The server or the API is not reachable.")

        if not self.api.is_minimum_version(response):
            return (False,
                    "The version of the wallabag instance is too old.")

        if self.api.api_token().has_error():
            return (False, response.error_description)

        return (True, "The config is suitable.")


class ConfigOption(ABC):

    prompt = ''
    default = ''

    def get_all(config):
        return [ServerurlOption(Api(config)), UsernameOption(),
                PasswordOption(), ClientOption(), SecretOption()]

    def __init__(self, default=None):
        self.set_default(default)

    def _check_existence_or_default(self, value):
        if not value:
            if not self.get_default():
                raise ValueError("Empty value")
            return self.get_default()
        return value

    def get_prompt(self):
        return self.prompt

    def get_default(self):
        return self.default

    def set_default(self, default):
        if default:
            self.default = default

    @abstractmethod
    def get_option_name(self):
        pass

    def check_and_apply(self, value):
        self.value = self._check_existence_or_default(value.strip())

    def get_value(self):
        return self.value

    def setup(self, config):
        (sec, opt) = self.get_option_name()
        self.set_default(config.get(sec, opt))
        value = click.prompt(self.get_prompt(),
                             default=self.get_default())
        try:
            self.check_and_apply(value)
        except ValueError as e:
            click.echo(e)
            return False
        config.set_config(sec, opt, self.get_value())
        return True


class ServerurlOption(ConfigOption):

    RE_HTTP = re.compile("(?i)https?:\\/\\/.+")

    prompt = 'Enter the url of your Wallabag instance'
    default = 'https://www.wallabag.com/'

    def __init__(self, api):
        self.api = api

    def __check_trailing_space(self, value):
        return value[:-1] if value[-1] == '/' else value

    def __check_https(self, value):
        return f"https://{value}" if not ServerurlOption.RE_HTTP.match(value)\
                else value

    def __check_api_verion(self, value):
        response = self.api.api_version(value)
        if response.has_error():
            raise ValueError(response.error_text)

        if not self.api.is_minimum_version(response):
            raise ValueError(
                    "Your wallabag instance is too old. \
                            You need at least version \
                            {api.MINIMUM_API_VERSION_HR}.")

    def check_and_apply(self, value):
        value = self._check_existence_or_default(value.strip())
        value = self.__check_trailing_space(value)
        value = self.__check_https(value)
        self.__check_api_verion(value)
        self.value = value

    def get_option_name(self):
        return (Sections.API, Options.SERVERURL)


class UsernameOption(ConfigOption):

    prompt = 'Enter your Wallabag username'

    def get_option_name(self):
        return (Sections.API, Options.USERNAME)


class PasswordOption(ConfigOption):

    prompt = 'Enter your Wallabag password'

    def get_option_name(self):
        return (Sections.API, Options.PASSWORD)


class ClientOption(ConfigOption):

    prompt = 'Enter the client id of your Wallabag API'

    def get_option_name(self):
        return (Sections.OAUTH2, Options.CLIENT)


class SecretOption(ConfigOption):

    prompt = 'Enter the client secret of your Wallabag API'

    def get_option_name(self):
        return (Sections.OAUTH2, Options.SECRET)
