from typing import Type, FrozenSet

from .constants import ErrorMessages
from .extension import Extension


class Extendable:
    _extensions = frozenset()

    @classmethod
    def with_extensions(cls, *extensions: Type[Extension]) -> Type["Extendable"]:
        """
        Returns a copy of the class with the provided extensions applied to it
        """

        def init_wrapper(self, *args, **kwargs):
            self._extension_data = {}  # Intended to temporarily hold metadata - can be modified by extensions
            yield

        class Extended(cls):
            pass

        Extended._extensions = frozenset(extensions)
        Extension.wrap(Extended, "__init__", init_wrapper)

        for extension_cls in Extended._extensions:
            if not issubclass(extension_cls, Extension):
                ErrorMessages.not_extension(extension_cls)

            if not extension_cls.can_extend(cls):
                ErrorMessages.invalid_extension(extension_cls)

            extension_cls.extend(Extended)

        return Extended

    @property
    def extensions(self) -> FrozenSet[Type[Extension]]:
        return self._extensions
