# -*- coding: utf-8 -*-

from abc import ABC


class Params(ABC):

    def validate(self):
        return True, None
