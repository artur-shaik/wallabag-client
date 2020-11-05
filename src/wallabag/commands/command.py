# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from wallabag.api.api import ApiException


class Command(ABC):

    params = None

    def __init__(self):
        self.log = logging.getLogger('wallabag.command')

    def execute(self):
        self.log.debug('executing command: %s', self.__class__.__name__)

        validated, msg = self.__validate()
        if not validated:
            return False, msg
        try:
            return self._run()
        except ApiException as ex:
            return False, str(ex)

    def __validate(self):
        if self.params:
            self.log.debug('validating parameters: %s', self.params.__dict__)

            return self.params.validate()
        return True, None

    @abstractmethod
    def _run(self):
        pass
