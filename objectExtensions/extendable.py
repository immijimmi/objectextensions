from inspect import getfullargspec
from types import MethodType
from typing import Sequence, Type, Tuple

from .constants import Keys, ErrorMessages
from .extension import Extension


class Extendable:
    def __init__(self, extensions: Sequence[Type[Extension]] = ()):
        self.__extensions = []
        self._extension_data = {}  # Intended to temporarily hold metadata - can be modified by extensions

        for extension_class in extensions:
            if not issubclass(extension_class, Extension):
                ErrorMessages.not_extension(extension_class)

            if not extension_class.can_extend(self):
                ErrorMessages.invalid_extension(extension_class)

            self.__extensions.append(extension_class)
            extension_class.extend(self)

    @property
    def extensions(self) -> Tuple[Type[Extension]]:
        return tuple(self.__extensions)
