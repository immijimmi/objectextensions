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
        raise TypeError("A provided extension does not inherit the base Extension class: {}".format(extension))

    @staticmethod
    def invalid_extension(extension):
        raise ValueError("A provided extension cannot be used to extend this class: {}".format(extension))

    @staticmethod
    def wrap_static(method_name):
        raise ValueError(
            ("Static class methods cannot be wrapped. "
             "The method must receive the object instance as 'self' for its first argument: {}").format(method_name))

    @staticmethod
    def duplicate_attribute(attribute_name):
        raise AttributeError(
            "The provided attribute name already exists on the target instance: {}".format(attribute_name))
