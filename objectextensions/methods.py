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
