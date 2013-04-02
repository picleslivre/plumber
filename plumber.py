# coding: utf-8
import abc
import Queue
import threading


__version__ = ('0', '1')


class UnmetPrecondition(Exception):
    pass


def precondition(precond):
    """
    Runs the callable responsible for making some assertions
    about the data structure expected for the transformation.

    If the precondition is not achieved, a UnmetPrecondition
    exception must be raised, and then the transformation pipe
    is bypassed.
    """
    def decorator(f):
        def decorated(instance, data):
            try:
                precond(data)
            except UnmetPrecondition:
                # bypass the pipe
                return data
            else:
                return f(instance, data)
        return decorated
    return decorator


class Pipe(object):
    """
    A segment of the transformation pipeline.

    ``transform`` method must return the transformation result.
    Sometimes a transformation process may need to fetch content
    from different endpoints, and it can be achieved through
    the ``fetch_resource`` method.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, data):
        """
        ``data`` must be an iterable
        """
        self._iterable_data = data

    def __iter__(self):
        """
        Iters through all items of ``self._iterable_data``, yielding its
        data already transformed.

        The iterable interface is the heart of the pipeline machinery.
        """
        for data in self._iterable_data:
            yield self.transform(data)

    @abc.abstractmethod
    def transform(self, data):
        """
        Performs the desired transformation to the data.
        """


class Pipeline(object):
    """
    Represents a chain of pipes (duh).

    ``*args`` are the pipes that will be executed in order
    to transform the input data.
    """
    def __init__(self, *args):
        self._pipes = args

    def run(self, data, rewrap=False, prefetch=0):
        """
        Wires the pipeline and returns a lazy object of
        the transformed data.

        ``data`` must be an iterable, where a full document
        must be returned for each loop

        ``rewrap`` is a bool that indicates the need to rewrap
        data in case iterating over it produces undesired data,
        for instance ``dict`` instances.

        ``prefetch`` is an int defining the number of items to
        be prefetched once the pipeline starts yielding data.
        """
        if rewrap:
            data = [data]

        for pipe in self._pipes:
            data = pipe(data)
        else:
            iterable = _prefetch(data, prefetch) if prefetch else data
            for out_data in iterable:
                yield out_data


def _prefetch(iterable, buff):
    def worker(job_queue, it):
        for item in it:
            job_queue.put(item)

        job_queue.put(None)

    job_queue = Queue.Queue(buff)
    thread = threading.Thread(target=worker, args=(job_queue, iter(iterable)))
    thread.daemon = True
    thread.start()

    while True:
        item = job_queue.get()
        if item is None:
            return
        else:
            yield item
