# -*- coding: utf-8 -*-

import base64
import configparser
import getpass
import logging
import os
import socket
import time
from pathlib import PurePath

from Crypto.Cipher import AES
from Crypto.Hash import MD5

from xdg.BaseDirectory import xdg_config_home as XDG_CONFIG_HOME


CONFIG_DIRECTORY = os.path.expanduser(XDG_CONFIG_HOME)
CONFIG_WALLABAG_DIR = "wallabag-cli"
CONFIG_FILENAME = "config.ini"


class Sections():
    API = "api"
    OAUTH2 = "oauth2"
    TOKEN = "token"


class Options():
    SERVERURL = "serverurl"
    USERNAME = "username"
    PASSWORD = "password"

    CLIENT = "client"
    SECRET = "secret"

    ACCESS_TOKEN = "access_token"
    EXPIRES = "expires"


class Configs():

    LOAD_ERROR =\
        """
        Error: Could not load or create the config file.
        """
    ENCRYPT_VALUES = [
            (Sections.API, Options.PASSWORD),
            (Sections.OAUTH2, Options.SECRET)]

    custom_path = None

    def __init__(self, path=None):
        self.log = logging.getLogger('wallabag.config')
        self.config = configparser.ConfigParser()
        self.load(path)

    def get_path(self, custom_path=None):
        if custom_path:
            self.custom_path = custom_path
        if self.custom_path:
            return PurePath(self.custom_path)
        return PurePath(CONFIG_DIRECTORY,
                        CONFIG_WALLABAG_DIR,
                        CONFIG_FILENAME)

    def set(self, section, name, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        if (section, name) in Configs.ENCRYPT_VALUES:
            value = self.__encrypt(value)
        self.config.set(section, name, value)

    def get(self, section, name, fallback=None):
        value = self.config.get(section, name, fallback=fallback)
        if value and (section, name) in Configs.ENCRYPT_VALUES:
            value = self.__decrypt(value)
        return value

    def getint(self, section, name, fallback=0):
        return self.config.getint(section, name, fallback=fallback)

    def getfloat(self, section, name, fallback=0):
        return self.config.getfloat(section, name, fallback=fallback)

    def is_token_expired(self):
        return self.getfloat('token', 'expires', 0) - time.time() < 0

    def is_valid(self):
        options_to_check = ((Sections.API, Options.SERVERURL),
                            (Sections.API, Options.USERNAME),
                            (Sections.API, Options.PASSWORD),
                            (Sections.OAUTH2, Options.CLIENT),
                            (Sections.OAUTH2, Options.SECRET))
        for s, o in options_to_check:
            if not self.config.has_option(s, o):
                return False
        return True

    def save(self, custom_path=None):
        path = self.get_path(custom_path)

        if not os.path.exists(path.parents[0]):
            os.makedirs(path.parents[0])
        with open(path, mode='w') as file:
            self.log.debug('writing config to: %s', path)

            self.config.write(file)

    def load(self, custom_path=None):
        path = self.get_path(custom_path)
        self.log.debug('loading config from: %s', path)
        try:
            self.config.read(path)
        except configparser.Error:
            self.log.exception("couldn't load config")
            raise ValueError(Configs.LOAD_ERROR)

    def load_or_create(self, custom_path=None):
        path = self.get_path(custom_path)

        success = False
        if not os.path.exists(path):
            success = self.save(path)
        else:
            success = self.load(path)
        if not success:
            raise ValueError(Configs.LOAD_ERROR)

    def __cryptkey(self):
        s1 = getpass.getuser()
        s2 = socket.gethostname()
        return MD5.new((s1 + s2).encode("utf-8")).digest()

    def __encrypt(self, value):
        try:
            cipher = AES.new(self.__cryptkey(), AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(value.encode('utf-8'))
            return "%s@%s@%s" % (
                    base64.b64encode(cipher.nonce).decode('utf-8'),
                    base64.b64encode(ciphertext).decode('utf-8'),
                    base64.b64encode(tag).decode('utf-8'))
        except Exception as e:
            print(e)
            ret = None
        return ret

    def __decrypt(self, value):
        try:
            nonce, ciphertext, tag = map(
                    lambda v: base64.b64decode(v), value.split('@'))
            cipher = AES.new(self.__cryptkey(), AES.MODE_EAX, nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except Exception as e:
            print(e)
            ret = None
        return ret
