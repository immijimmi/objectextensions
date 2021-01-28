# Object Extensions

###### A basic framework for implementing an extension pattern

## Quickstart

### Setup

Below is an example of an extendable class, and an example extension that can be applied to it.

```python
from objectextensions import Extendable


class HashList(Extendable):
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
        Extension._set(target_cls, "increment_append_count", Listener._increment_append_count)

        Extension._wrap(target_cls, "__init__", Listener._wrap_init)
        Extension._wrap(target_cls, 'append', Listener._wrap_append)

    def _increment_append_count(self):
        self.append_count += 1

    def _wrap_init(self, *args, **kwargs):
        Extension._set(self, "append_count", 0)
        yield

    def _wrap_append(self, *args, **kwargs):
        yield
        self.increment_append_count()
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
>>> my_hashlist.append(7)  # Listener has wrapped this to increment .append_count
>>> my_hashlist.append_count
4
```

## Functionality

### Properties

Extendable.**extensions**  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a reference to a frozenset containing the applied extensions.  
&nbsp;

### Methods

Extendable.**with_extensions**(*cls, \*extensions: Type[Extension]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a copy of the class with the provided extensions applied to it.  
&nbsp;

Extension.**can_extend**(*target_cls: Type[Extendable]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Abstract staticmethod which must be overridden.  
&nbsp;&nbsp;&nbsp;&nbsp;Should return a bool indicating whether this Extension can be applied to the target class.  
&nbsp;

Extension.**extend**(*target_cls: Type[Extendable]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Abstract staticmethod which can be overridden.  
&nbsp;&nbsp;&nbsp;&nbsp;Any modification of the target **class** should take place in this function.  
&nbsp;

Extension.**\_wrap**(*target_cls: Type[Extendable], method_name: str,*  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*gen_func: Callable[[Extendable, Any, Any], Generator[None, Any, None]]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Used to wrap an existing method on the target class.  
&nbsp;&nbsp;&nbsp;&nbsp;Passes copies of the method parameters to the generator function provided.  
&nbsp;&nbsp;&nbsp;&nbsp;The generator function should yield once,  
&nbsp;&nbsp;&nbsp;&nbsp;with the yield statement receiving a copy of the result of executing the core method.  
&nbsp;

Extension.**\_set**(*target: Union[Type[Extendable], Extendable], attribute_name: str, value: Any*)  
&nbsp;&nbsp;&nbsp;&nbsp;Used to safely add new attributes to an extendable class or instance. In contrast with assigning them directly,  
&nbsp;&nbsp;&nbsp;&nbsp;this method will raise an error if the attribute already exists (for example, if another extension added it)  
&nbsp;&nbsp;&nbsp;&nbsp;to ensure compatibility issues are flagged and can be dealt with easily.  
&nbsp;

## Additional Info

- As extensions do not properly invoke name mangling, adding private members via extensions is discouraged; doing so may lead to unintended behaviour.
Using protected members instead is encouraged, as name mangling does not come into play in this case.
