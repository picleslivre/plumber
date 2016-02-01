==============
picles.plumber
==============

A simple data transformation pipeline based on python's iteration protocol that
runs on python versions 2.7, 3.3 and 3.4.

.. code-block::

     +----------+      +-------------+      +-------------+      +--------+      +----------+
     | Producer | ---> | Transformer | ---> | Transformer | ---> | Tester | ---> | Consumer |
     +----------+      +-------------+      +-------------+      +--------+      +----------+



A pipeline model expects 4 types of filters:

* Producer: starting point, outbound only;
* Transformer: input, processing, output;
* Tester: input, discard or pass-thru;
* Consumer: ending point, inbound only.


.. code-block:: python

    import plumber
    
    @plumber.filter
    def upper(data):
        return data.upper()
    
    ppl = plumber.Pipeline(upper)
    output = ppl.run("Hey Jude, don't make it bad")
    
    print(''.join(output))
    "HEY JUDE, DON'T MAKE IT BAD"


Since the design is based on python's iteration protocol, both producers and 
consumers are ordinary iterable objects. Transformers are implemented as 
callables that accept a single argument, perform the processing and return the 
result. 

Input data may also be checked against some preconditions in order to decide 
if the transformation should happen or be by-passed. For example:


.. code-block:: python

    import plumber
    
    def is_vowel(data):
        if data not in 'aeiou':
            raise plumber.UnmetPrecondition()
    
    @plumber.filter
    @plumber.precondition(is_vowel)
    def upper(data):
        return data.upper()
    
    ppl = plumber.Pipeline(upper)
    output = ppl.run("Hey Jude, don't make it bad")
    
    print(''.join(output))
    "hEy jUdE, dOn't mAkE It bAd"


Prefetching
-----------

If you think the pipes are taking too long to move data forward, 
you can use a prefetching feature. To use it, just define the upper 
limit of items to be pre fetched.

Using the same example as above:


.. code-block:: python

    ppl = plumber.Pipeline(stripper, upper)
    transformed_data = ppl.run([" I am the Great Cornholio!", "Hey Jude, don't make it bad "], 
                               prefetch=2)
    
    for td in transformed_data:
        print(td)
    
    I AM THE GREAT CORNHOLIO!
    "HEY JUDE, DON'T MAKE IT BAD"


By default the prefetching mechanism is thread-based, so be careful with cpu-bound
pipelines.


Installation
------------

Pypi (recommended):

.. code-block:: bash

    $ pip install picles.plumber


Source code (development version):

.. code-block:: bash

    $ git clone https://github.com/picleslivre/plumber.git && cd plumber && python setup.py install


Use license
-----------

This project is licensed under FreeBSD 2-clause. See `LICENSE <https://github.com/picleslivre/plumber/blob/master/LICENSE>`_ for more details.

