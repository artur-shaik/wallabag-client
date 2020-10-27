# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod


class Command(ABC):

    def __init__(self):
        self.log = logging.getLogger('wallabag.command')

    def execute(self):
        self.log.debug('executing command: %s', self.__class__.__name__)

        validated, msg = self.__validate()
        if not validated:
            return False, msg
        return self._run()

    def __validate(self):
        if self.params:
            self.log.debug('validating parameters: %s', self.params.__dict__)

            return self.params.validate()
        return True, None

    @abstractmethod
    def _run(self):
        pass
