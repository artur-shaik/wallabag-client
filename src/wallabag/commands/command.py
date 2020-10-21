# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class Command(ABC):

    def execute(self):
        validated, msg = self.__validate()
        if not validated:
            return False, msg
        return self._run()

    def __validate(self):
        if self.params:
            return self.params.validate()
        return True, None

    @abstractmethod
    def _run(self):
        pass
