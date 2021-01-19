import pytest
from inspect import getfullargspec

from objectExtensions import Extendable, Extension


@pytest.fixture
def res():
    class HashList(Extendable):
        def __init__(self, iterable=(), extensions=()):
            super().__init__(extensions=extensions)

            self.values = {}
            self.list = []

            for value in iterable:
                self.append(value)

        def append(self, item):
            self.list.append(item)
            self.values[item] = self.values.get(item, []) + [len(self.list) - 1]

        def index(self, item):
            if item not in self.values:
                raise ValueError("{0} is not in hashlist".format(item))

            return self.values[item]

        def __contains__(self, item):
            return item in self.values

    class Listener(Extension):
        @staticmethod
        def can_extend(target_cls):
            return target_cls is HashList

        @staticmethod
        def extend(target_cls):
            target_cls.append_count = 0
            target_cls.increment_append_count = Listener._increment_append_count

            Extension.wrap(target_cls, 'append', Listener._append_wrapper)

        @staticmethod
        def _append_wrapper(metadata):
            yield
            metadata["self"].increment_append_count()

        def _increment_append_count(self):
            self.append_count += 1

    return {"hashlist": HashList, "listener": Listener}


class TestHashlist:
    def test_error_raised_if_can_extend_returns_false(self, res):
        class Plus(Extension):
            @staticmethod
            def can_extend(target_instance):
                return False

            @staticmethod
            def extend(target_instance):
                pass

        pytest.raises(ValueError, res["hashlist"], extensions=[Plus])

    def test_correct_extensions_returned(self, res):
        instance = res["hashlist"](extensions=[res["listener"]])

        assert tuple(instance.extensions) == (res["listener"],)

    def test_method_correctly_bound(self, res):
        instance = res["hashlist"](extensions=[res["listener"]])

        assert instance.append_count == 0

        instance.increment_append_count()

        assert instance.append_count == 1

    def test_listener_increments_counter_on_append(self, res):
        instance = res["hashlist"](extensions=[res["listener"]])

        instance.append(5)
        instance.append(3)

        assert instance.append_count == 2

        instance.index(5)

        assert instance.append_count == 2

    def test_wrap_preserves_method_signature(self, res):
        def dummy_method(self, arg_1, arg_2, kwarg_1=1, kwarg_2=2):
            pass

        def dummy_wrapper(metadata):
            yield

        class Plus(Extension):
            @staticmethod
            def can_extend(target_instance):
                return True

            @staticmethod
            def extend(target_instance):
                target_instance.method = dummy_method
                Extension.wrap(target_instance, "method", dummy_wrapper)

        instance = res["hashlist"](extensions=[Plus])

        expected_spec = getfullargspec(dummy_method)
        actual_spec = getfullargspec(instance.method)

        assert actual_spec is not expected_spec
        assert actual_spec == expected_spec
