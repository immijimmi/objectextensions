from wrapt import decorator

from inspect import getfullargspec
from copy import deepcopy
from typing import Generator, Callable, Any, Dict

from .constants import Keys, ErrorMessages


class Extension:
    @staticmethod
    def extend(target_cls: "Extendable") -> None:
        """
        Any modification of the target class should take place in this function
        """

        raise NotImplementedError

    @staticmethod
    def can_extend(target_cls: "Extendable") -> bool:
        """
        Should return a bool indicating whether this Extension can be applied to the target class
        """

        raise NotImplementedError

    @staticmethod
    def wrap(target_cls: "Extendable", method_name: str,
             gen_func: Callable[[Dict], Generator[None, Any, None]]) -> None:
        """
        Used to wrap an existing method on the target class.
        Passes a metadata object to the generator function provided.
        The metadata object is structured as follows:
        {
            "self": <a reference to target_instance>,
            "extension_data": <a copy of the _extension_data property of target_instance prior to running the method>,
            "args": <a copy of the args which get passed into the method>,
            "kwargs": <a copy of the kwargs which get passed into the method>,
        }
        Note that only copies of metadata values are provided to the generator function,
        as the wrapper should not modify the functionality of the core method.
        The generator function should yield once,
        with the yield statement receiving a copy of the result of executing the core method.
        """

        method = getattr(target_cls, method_name)
        method_args = getfullargspec(method).args

        if len(method_args) == 0 or method_args[0] != Keys.self:
            ErrorMessages.wrap_static(method_name)

        @decorator  # This will preserve the original method signature when wrapping the method
        def wrapper(func, self, args, kwargs):
            metadata = {
                Keys.self: self,
                Keys.extension_data: deepcopy(self._extension_data),
                Keys.args: deepcopy(args),
                Keys.kwargs: deepcopy(kwargs)
                }
            
            gen = gen_func(metadata)
            next(gen)

            result = func(*args, **kwargs)

            try:
                gen.send(deepcopy(result))
            except StopIteration:
                pass

            return result

        setattr(target_cls, method_name, wrapper(method))
