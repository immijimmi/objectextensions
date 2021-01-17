from inspect import getfullargspec
from types import MethodType
from typing import Sequence, Type, Tuple

from .constants import Keys, ErrorMessages
from .extension import Extension


class Extendable:
    def __init__(self, extensions: Sequence[Type[Extension]] = ()):
        self.__extensions = []
        self._extension_data = {}

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

    def __setattr__(self, name, value):
        if callable(value):
            func_args = getfullargspec(value).args

            """
            In order to set a new instance method, any function provided
            must expose `self` as its first parameter.
            """
            if len(func_args) > 0 and func_args[0] == Keys.self:
                value = MethodType(value, self)

            # TODO: Add support for classmethods

        self.__dict__[name] = value
