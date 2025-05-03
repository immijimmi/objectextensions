from typing import Type, Tuple
from abc import ABC

from .extension import Extension
from .methods import Methods, Decorators, ErrorMessages


class Extendable(ABC):
    _extensions = tuple()

    def __init__(self):
        # Intended to temporarily hold metadata - can be modified in methods attached by extensions
        self._extension_data = {}

    @property
    def extension_data(self) -> dict:
        """
        Returns a snapshot of the instance's extension data.
        This is intended to hold metadata optionally provided by extensions for the sake of introspection,
        and for communication between extensions
        """

        return Methods.try_copy(self._extension_data)

    @Decorators.classproperty
    def extensions(cls) -> Tuple[Type[Extension]]:
        """
        Returns a tuple of any extensions that have been applied to this class, in order of application
        """

        return cls._extensions

    @classmethod
    def with_extensions(cls, *extensions: Type[Extension]) -> Type["Extendable"]:
        """
        Returns a subclass with the provided extensions applied to it
        """

        if not extensions:
            return cls

        # Generating a subclass to apply extensions to
        result = type(
            f"{cls.__name__}.with_extensions({', '.join(extension_cls.__name__ for extension_cls in extensions)})",
            (cls,),
            {}
        )

        # Applying the provided extensions
        for extension_cls in extensions:
            if not issubclass(extension_cls, Extension):
                ErrorMessages.not_extension(extension_cls)

            if not extension_cls.can_extend(cls):
                ErrorMessages.invalid_extension(extension_cls)

            extension_cls.extend(result)
            result._extensions = (*result._extensions, extension_cls)

        return result
