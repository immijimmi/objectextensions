from typing import Any
from copy import deepcopy


class Methods:
    @staticmethod
    def try_copy(item: Any) -> Any:
        """
        A failsafe deepcopy wrapper
        """

        try:
            return deepcopy(item)
        except:
            return item


class Decorators:
    @staticmethod
    def classproperty(func):
        class CustomDescriptor:
            def __get__(self, instance, owner):
                return func(owner)

            def __set__(self, instance, value):
                raise AttributeError("can't set attribute")

        return CustomDescriptor()


class ErrorMessages:
    @staticmethod
    def not_extension(extension):
        raise TypeError(f"a provided extension does not inherit from the `Extension` class: {extension}")

    @staticmethod
    def invalid_extension(extension):
        raise ValueError(f"a provided extension cannot be used to extend this class: {extension}")

    @staticmethod
    def wrap_static(method_name):
        raise ValueError(
            f"static class methods cannot be wrapped; the provided method `{method_name}` "
            "must have `self` for its first parameter"
        )

    @staticmethod
    def duplicate_attribute(attribute_name):
        raise AttributeError(f"the provided attribute name already exists on the target instance: {attribute_name}")
