# scielo.plumber

A simple data transformation pipeline.


## Installation

```bash
pip install scielo.plumber
```


## Basic usage

```python
import plumber


class StripPipe(plumber.Pipe):
    def transform(self, data):
        return data.strip()

class UpperPipe(plumber.Pipe):
    def transform(self, data):
        return data.upper()

ppl = plumber.Pipeline(StripPipe(), UpperPipe())
transformed_data = ppl.run([" I am the Great Cornholio!", "Hey Jude, don't make it bad "])

for td in transformed_data:
    print(td)

I AM THE GREAT CORNHOLIO!
HEY JUDE, DON'T MAKE IT BAD
```


## Prefetching

If you think the pipes are taking too long to move data forward, 
you can use a prefetching feature. To use it, just define the upper 
limit of items to be pre fetched.

Using the same example as above:

```python
ppl = plumber.Pipeline(StripPipe(), UpperPipe())
transformed_data = ppl.run([" I am the Great Cornholio!", "Hey Jude, don't make it bad "], 
                           prefetch=2)

for td in transformed_data:
    print(td)

I AM THE GREAT CORNHOLIO!
HEY JUDE, DON'T MAKE IT BAD
```


## Preconditions

As the name suggests, a precondition is used to test if a pipe can be processed, 
before being processed. It is implemented as a function that receives the pipe input
and performs some validation raising `UnmetPrecondition` or returning `None`.


```python
from plumber import Pipe, precondition, UnmetPrecondition

def is_text(data):
    if not isinstance(data, basestring):
        raise UnmetPrecondition()

@precondition(is_text)
class StripPipe(plumber.Pipe):
    def transform(self, data):
        return data.strip()
```

## Links

* IRC: #scielo @ freenode
* Mailing list: scielo-dev@googlegroups.com


## Use license

This project is licensed under FreeBSD 2-clause. See `LICENSE` for more details.

