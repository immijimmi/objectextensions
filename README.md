# Object Extensions

###### A basic framework for implementing an extension pattern

## Quickstart

### Setup

Below is an example of an extendable class, and an example extension that can be applied to it.

```python
from objectextensions import Extendable


class HashList(Extendable):
    def __init__(self, iterable=()):
        self.values = {}
        self.list = []

        for value in iterable:
            self.append(value)

    def append(self, item):
        self.list.append(item)
        self.values[item] = self.values.get(item, []) + [len(self.list) - 1]

    def index(self, item):
        """
        Returns all indexes containing the specified item.
        Much lower time complexity than a typical list due to dict lookup usage
        """

        if item not in self.values:
            raise ValueError("{0} is not in hashlist".format(item))

        return self.values[item]
```
```python
from objectextensions import Extension


class Listener(Extension):
    @staticmethod
    def can_extend(target_cls):
        return issubclass(target_cls, HashList)

    @staticmethod
    def extend(target_cls):
        target_cls.increment_append_count = Listener._increment_append_count

        Extension.wrap(target_cls, "__init__", Listener._wrap_init)
        Extension.wrap(target_cls, 'append', Listener._wrap_append)

    def _increment_append_count(self):
        self.append_count += 1

    def _wrap_init(self, *args, **kwargs):
        self.append_count = 0
        yield

    def _wrap_append(self, *args, **kwargs):
        yield
        self.increment_append_count()
```

### Instantiation
```python
my_list = HashList.with_extensions(Listener)(iterable=[5,2,4])
```

### Result
```python
>>> my_list.append_count  # Attribute that was added by the Listener extension
3
>>> my_list.append(7)  # Listener has wrapped this to increment .append_count
>>> my_list.append_count
4
```
