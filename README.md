# Object Extensions

###### A basic framework for implementing an extension pattern

## Summary

The point of this framework is to provide a more modular alternative to object inheritance.

**Consider the following use case:** You have an abstract class `Car` intended to represent a generic real-world car, and need a pattern that allows you to *optionally* add more features to it.
For example, you may want to add a convertible roof or a touchscreen on the dashboard, but these features will not necessarily be added to every subclass of `Car` you create.

Applying standard OOP here means you would need to make a subclass every time a new combination of these optional features is needed.
In the above case, you may need one subclass for a car with a convertible roof, one subclass for a car with a touchscreen, and one that has both features. As the amount of optional features increases,
the amount of possible combinations skyrockets. This is not a scalable solution to the problem.

Object Extensions is an elegant way to handle scenarios such as this one. Rather than creating a new subclass for each possible combination,
you create one extension representing each feature. When you need to create an instance of a car with a particular set of features,
take the parent class and pass it the exact set of extensions you want to apply via the `.with_extensions()` method.

Note that this pattern is intended to be used alongside inheritance, not to replace it entirely. The two can be mixed without issue, such that
(for example) a subclass could extend a parent class that has pre-applied extensions like so:
```python
class SpecificCarModel(Car.with_extensions(TouchscreenDash)):
    pass
```

## Quickstart

### Setup

Below is an example of an extendable class, and an example extension that can be applied to it.

```python
from objectextensions import Extendable


class HashList(Extendable):
    """
    A basic example class with some data and methods.
    Inheriting Extendable allows this class to be modified with extensions
    """

    def __init__(self, iterable=()):
        super().__init__()

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
        Much lower time complexity than in a typical list due to dict lookup usage
        """

        if item not in self.values:
            raise ValueError(f"{item} is not in hashlist")

        return self.values[item]
```
```python
from objectextensions import Extension


class Listener(Extension):
    """
    This extension class is written to apply a counter to the HashList class,
    which increments any time .append() is called
    """

    @staticmethod
    def can_extend(target_cls):
        return issubclass(target_cls, HashList)

    @staticmethod
    def extend(target_cls):
        Extension._set(target_cls, "increment_append_count", Listener.__increment_append_count)

        Extension._wrap(target_cls, "__init__", Listener.__wrap_init)
        Extension._wrap(target_cls, 'append', Listener.__wrap_append)

    def __wrap_init(self, *args, **kwargs):
        Extension._set(self, "append_count", 0)
        yield

    def __wrap_append(self, *args, **kwargs):
        yield
        self.increment_append_count()

    def __increment_append_count(self):
        self.append_count += 1
```

### Instantiation
```python
HashListWithListeners = HashList.with_extensions(Listener)
my_hashlist = HashListWithListeners(iterable=[5,2,4])
```
or, for shorthand:
```python
my_hashlist = HashList.with_extensions(Listener)(iterable=[5,2,4])
```

### Result
```python
>>> my_hashlist.append_count  # Attribute that was added by the Listener extension
3
>>> my_hashlist.append(7)  # Listener has wrapped this method with logic which increments `.append_count`
>>> my_hashlist.append_count
4
```

## Additional Info

- As extensions do not currently invoke name mangling, adding private members (names which begin with double underscores)
to Extendable classes via extensions is discouraged; doing so may lead to unintended behaviour.
Using protected members (names with a single leading underscore) instead is encouraged, as name mangling does not come into play in this case.
