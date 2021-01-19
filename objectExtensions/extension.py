from wrapt import decorator

from inspect import getfullargspec
from copy import deepcopy
from typing import Callable

from .constants import Keys, ErrorMessages


class Extension:
    @staticmethod
    def extend(target_cls: "Extendable") -> None:
        """
        Any modification of an object which implements Extendable should take place in this function
        """

        raise NotImplementedError

    @staticmethod
    def can_extend(target_cls: "Extendable") -> bool:
        """
        Should return a bool indicating whether this Extension can be applied to target_instance
        """

        raise NotImplementedError

    @staticmethod
    def wrap(target_cls: "Extendable", method_name: str,
             before: Callable = lambda metadata: None, after: Callable = lambda metadata: None) -> None:
        """
        Used to wrap an existing method on target_instance.
        Passes a metadata object to any function provided either as the 'before' or the 'after' parameter.
        The metadata object is structured as follows:
        {
            "self": <a reference to target_instance>,
            "extension_data": <a copy of the _extension_data property of target_instance prior to running the method>,
            "args": <a copy of the args which get passed into the method>,
            "kwargs": <a copy of the kwargs which get passed into the method>,
            "result": <a copy of the value returned by the method (only available to the 'after' parameter)>
        }
        Note that only copies are provided to wrapper functions,
        as they are not meant to modify the functionality of the core method
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
            
            before(metadata)
            result = func(*args, **kwargs)

            metadata[Keys.result] = deepcopy(result)
            after(metadata)

            return result

        setattr(target_cls, method_name, wrapper(method))
