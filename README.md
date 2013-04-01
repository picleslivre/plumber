plumber
=======

A simple data transformation pipeline.


Installation::

```bash
pip install -e git+git://github.com/gustavofonseca/plumber.git#egg=plumber
```


Usage example::

```python
import plumber


class StripPipe(plumber.Pipe):
    def transform(self, data):
        return data.strip()

class UpperPipe(plumber.Pipe):
    def transform(self, data):
        return data.upper()

ppl = plumber.Pipeline(StripPipe, UpperPipe)
transformed_data = ppl.run([" I am the Great Cornholio!"])

for td in transformed_data:
    print(td)

I AM THE GREAT CORNHOLIO!
```