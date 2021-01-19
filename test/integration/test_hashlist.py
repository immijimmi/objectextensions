import pytest

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
            def increment_append_count(self):
                self.append_count += 1

            target_cls.append_count = 0
            target_cls.increment_append_count = increment_append_count

            Extension.wrap(target_cls, 'append', after=lambda metadata: metadata["self"].increment_append_count())

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

    def test_listener_increments_counter_on_append(self, res):
        instance = res["hashlist"](extensions=[res["listener"]])

        assert instance.append_count == 0

        instance.append(5)
        instance.append(3)

        assert instance.append_count == 2

        instance.index(5)

        assert instance.append_count == 2
