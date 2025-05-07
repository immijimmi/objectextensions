from wrapt import decorator

from inspect import getfullargspec
from typing import Generator, Callable, Any, Optional, Type
from abc import ABC

from .methods import Methods


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
    def _wrap(
            target_cls: Type["Extendable"], method_name: str,
            wrapper: Callable[..., Generator[None, Any, None]]
    ) -> None:
        """
        Used to wrap an existing method on the target class with surrounding functionality. The provided wrapper
        should be a generator function.

        The wrapper will receive copies of the arguments being passed into the invoked method,
        and should yield exactly once.

        Any code *before* the yield statement will be executed before the wrapped method,
        and any code *after* the yield statement will be executed after the wrapped method.

        The yield statement itself will receive a copy of the value returned by the wrapped method
        """

        target_method = getattr(target_cls, method_name)

        setattr(target_cls, method_name, Extension.__create_wrapped_method(target_method, wrapper))

    @staticmethod
    def _wrap_property(
            target_cls: Type["Extendable"], property_name: str,
            getter_wrapper: Optional[Callable[..., Generator[None, Any, None]]] = None,
            setter_wrapper: Optional[Callable[..., Generator[None, Any, None]]] = None,
            deleter_wrapper: Optional[Callable[..., Generator[None, Any, None]]] = None,
    ) -> None:
        """
        Used to wrap any combination of the getter, setter and deleter methods of a property on the target class with
        surrounding functionality
        """

        target_prop = getattr(target_cls, property_name)
        target_prop_methods = [target_prop.fget, target_prop.fset, target_prop.fdel]
        target_prop_docstring = target_prop.__doc__

        for wrapper_index, wrapper in enumerate((getter_wrapper, setter_wrapper, deleter_wrapper)):
            method = target_prop_methods[wrapper_index]

            if wrapper is not None:
                if method is None:
                    raise AttributeError(
                        f"property `{property_name}` does not have a"
                        f" {("getter", "setter", "deleter")[wrapper_index]} method to be wrapped"
                    )

                target_prop_methods[wrapper_index] = Extension.__create_wrapped_method(method, wrapper)

        setattr(
            target_cls, property_name,
            property(
                fget=target_prop_methods[0],
                fset=target_prop_methods[1],
                fdel=target_prop_methods[2],
                doc=target_prop_docstring)
        )

    @staticmethod
    def _set(target_cls: Type["Extendable"], attribute_name: str, value: Any) -> None:
        """
        Used to safely add a new attribute to an extendable class.

        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily
        """

        if hasattr(target_cls, attribute_name):
            raise AttributeError(f"attribute `{attribute_name}` already exists on the target class")

        setattr(target_cls, attribute_name, value)

    @staticmethod
    def _set_property(
            target_cls: Type["Extendable"], property_name: str,
            getter: Optional[Callable[["Extendable"], Any]] = None,
            setter: Optional[Callable[["Extendable", Any], None]] = None,
            deleter: Optional[Callable[["Extendable"], None]] = None,
            docstring: Optional[str] = None
    ) -> None:
        """
        Used to safely add a new property to an extendable class. Any combination of getter, setter and
        deleter may be provided, along with a docstring for the property.

        Will raise an error if the attribute already exists (for example, if another extension has already added it)
        to ensure compatibility issues are flagged and can be dealt with easily
        """

        if hasattr(target_cls, property_name):
            raise AttributeError(f"attribute `{property_name}` already exists on the target class")

        setattr(
            target_cls, property_name,
            property(fget=getter, fset=setter, fdel=deleter, doc=docstring)
        )

    @staticmethod
    def __create_wrapped_method(method, wrapper_gen_func):
        method_args = getfullargspec(method).args
        if len(method_args) == 0 or method_args[0] != "self":
            raise ValueError(
                f"static or class methods cannot be wrapped;"
                " the provided method must have `self` for its first parameter"
            )

        @decorator  # This will preserve the original method signature when wrapping the method
        def wrapper(func, self, args, kwargs):
            gen = wrapper_gen_func(self, *Methods.try_copy(args), **Methods.try_copy(kwargs))
            next(gen)

            result = func(*args, **kwargs)

            try:
                gen.send(Methods.try_copy(result))
            except StopIteration:
                pass

            return result

        return wrapper(method)
