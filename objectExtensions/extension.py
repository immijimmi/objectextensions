from wrapt import decorator

from inspect import getfullargspec
from types import MethodType
from copy import deepcopy
from typing import Callable, Any

from .constants import Keys, ErrorMessages


class Extension:
    @staticmethod
    def extend(target_instance: "Extendable") -> None:
        """
        Any modification of an object which implements Extendable should take place in this function
        """

        raise NotImplementedError

    @staticmethod
    def can_extend(target_instance: "Extendable") -> bool:
        """
        Should return a bool indicating whether this Extension can be applied to target_instance
        """

        raise NotImplementedError

    @staticmethod
    def wrap(target_instance: "Extendable", method_name: str,
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

        method = getattr(target_instance, method_name)
        method_args = getfullargspec(method).args

        if len(method_args) == 0 or method_args[0] != Keys.self:
            ErrorMessages.wrap_static(method_name)

        @decorator
        def wrapper(func, self, args, kwargs):
            metadata = {
                Keys.self: self,
                Keys.extension_data: Extension._try_copy(self._extension_data),
                Keys.args: Extension._try_copy(args),
                Keys.kwargs: Extension._try_copy(kwargs)
                }
            
            before(metadata)
            result = func(*args, **kwargs)

            metadata[Keys.result] = Extension._try_copy(result)
            after(metadata)

            return result

        target_instance.__dict__[method_name] = wrapper(method)

    @staticmethod
    def set(target_instance: "Extendable", attribute_name: str, value: Any) -> None:
        """
        This function should be used instead of directly setting attributes on target_instance,
        to allow handling of any duplication of members due to multiple extensions choosing the same attribute name.
        It will also handle binding new methods to the instance
        """

        if attribute_name in dir(target_instance):
            ErrorMessages.duplicate_attribute(attribute_name)

        if callable(value):
            func_args = getfullargspec(value).args

            """
            In order to set a new instance method, any function provided
            must expose `self` as its first parameter.
            """
            if len(func_args) > 0 and func_args[0] == Keys.self:
                value = MethodType(value, target_instance)

            # TODO: Add support for classmethods

        setattr(target_instance, attribute_name, value)

    @staticmethod
    def _try_copy(item: Any) -> Any:
        """
        Used internally as a failsafe in case an item cannot be deepcopied
        """

        try:
            return deepcopy(item)
        except:
            return item
