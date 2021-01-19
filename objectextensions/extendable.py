from typing import Sequence, Type, FrozenSet

from .constants import ErrorMessages
from .extension import Extension


class Extendable:
    def __new__(cls, extensions):
        cls.__extensions = frozenset(extensions)
        cls._extension_data = {}  # Intended to temporarily hold metadata - can be modified by extensions

        for extension_cls in cls.__extensions:
            if not issubclass(extension_cls, Extension):
                ErrorMessages.not_extension(extension_cls)

            if not extension_cls.can_extend(cls):
                ErrorMessages.invalid_extension(extension_cls)

            extension_cls.extend(cls)

        return super().__new__(cls)

    def __init__(self, extensions: Sequence[Type[Extension]] = ()):
        pass

    @property
    def extensions(self) -> FrozenSet[Type[Extension]]:
        return self.__extensions
