from wrapt import decorator

from inspect import getfullargspec
from typing import Generator, Callable, Any, Union, Type
from abc import ABC

from .methods import Methods, ErrorMessages


class Extension(ABC):
    @staticmethod
    def can_extend(target_cls: Type["Extendable"]) -> bool:
        """
        Should return a bool indicating whether this Extension can be applied to the target class
        """

        raise NotImplementedError

    @staticmethod
    def extend(target_cls: Type["Extendable"]) -> None:
        """
        Any modification of the target class should take place in this function
        """

        raise NotImplementedError

    @staticmethod
    def _wrap(target_cls: Type["Extendable"], method_name: str,
              gen_func: Callable[..., Generator[None, Any, None]]) -> None:
        """
        Used to wrap an existing method on the target class with surrounding functionality.

        The provided generator function will receive copies of the arguments being passed into the invoked method,
        and should yield exactly once.

        Any code *before* the yield statement inside this generator function will be executed before the wrapped method,
        and any code *after* the yield statement will be executed after the wrapped method.
        The yield statement itself will receive a copy of the value returned by the wrapped method
        """

        method = getattr(target_cls, method_name)
        method_args = getfullargspec(method).args

        if len(method_args) == 0 or method_args[0] != "self":
            ErrorMessages.wrap_static(method_name)

        @decorator  # This will preserve the original method signature when wrapping the method
        def wrapper(func, self, args, kwargs):
            gen = gen_func(self, *Methods.try_copy(args), **Methods.try_copy(kwargs))
            next(gen)

            result = func(*args, **kwargs)

            try:
                gen.send(Methods.try_copy(result))
            except StopIteration:
                pass

            return result

        setattr(target_cls, method_name, wrapper(method))

    @staticmethod
    def _set(target: Union[Type["Extendable"], "Extendable"], attribute_name: str, value: Any) -> None:
        """
        Used to safely add a new attribute to an extendable class.

        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily.

        Note: It is possible but not recommended to modify an instance rather than a class using this method
        """

        if hasattr(target, attribute_name):
            ErrorMessages.duplicate_attribute(attribute_name)

        setattr(target, attribute_name, value)

    @staticmethod
    def _set_property(
            target: Union[Type["Extendable"], "Extendable"], property_name: str,
            value: Callable[["Extendable"], Any]
    ) -> None:
        """
        Used to safely add a new property to an extendable class.

        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily.

        Note: It is possible but not recommended to modify an instance rather than a class using this method
        """

        Extension._set(target, property_name, value)

        setattr(
            target, property_name,
            property(getattr(target, property_name))
        )

    @staticmethod
    def _set_setter(
            target: Union[Type["Extendable"], "Extendable"], setter_name: str, linked_property_name: str,
            value: Callable[["Extendable", Any], Any]
    ) -> None:
        """
        Used to safely add a new setter to an extendable class.

        If the property this setter is paired with does not use the same attribute name,
        and the setter's name already exists on the class (for example, if another extension has already added it),
        an error will be raised.
        This is to ensure compatibility issues are flagged and can be dealt with easily.

        Note: It is possible but not recommended to modify an instance rather than a class using this method
        """

        if (not setter_name == linked_property_name) and hasattr(target, setter_name):
            ErrorMessages.duplicate_attribute(setter_name)

        setattr(
            target, setter_name,
            getattr(target, linked_property_name).setter(value)
        )
