from wrapt import decorator

from inspect import getfullargspec
from typing import Generator, Callable, Any, Union, Type

from .constants import ErrorMessages
from .methods import Methods


class Extension:
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

        pass

    @staticmethod
    def _wrap(target_cls: Type["Extendable"], method_name: str,
              gen_func: Callable[["Extendable", ...], Generator[None, Any, None]]) -> None:
        """
        Used to wrap an existing method on the target class.
        Passes copies of the method parameters to the generator function provided.
        The generator function should yield once,
        with the yield statement receiving a copy of the result of executing the core method
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
        Used to safely add a new attribute to an extendable class or instance.
        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily
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
        Used to safely add a new property to an extendable class or instance.
        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily
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
        Used to safely add a new setter to an extendable class or instance.
        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily
        """

        Extension._set(target, setter_name, value)
        setattr(
            target, setter_name,
            getattr(target, linked_property_name).setter(getattr(target, setter_name))
        )
