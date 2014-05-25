# coding: utf-8
import abc
try:
    from queue import Queue
except ImportError:  # PY2
    from Queue import Queue
import threading
import multiprocessing
import types
import logging


__version__ = ('0', '9')
__all__ = ['UnmetPrecondition', 'Pipe', 'Pipeline', 'precondition']


logger = logging.getLogger(__name__)


class UnmetPrecondition(Exception):
    pass


class ThreadSafeIter(object):
    """
    Wraps an iterable for safe use in a threaded environment.
    """
    def __init__(self, it):
        self.it = iter(it)
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.it)
    next = __next__


def thread_based_prefetch(iterable, buff):

    def worker(job_queue, it):
        for item in it:
            job_queue.put(item)

        job_queue.put(None)

    max_threads = multiprocessing.cpu_count() * 2
    total_threads = buff if buff < max_threads else max_threads

    running_threads = []
    job_queue = Queue(buff)
    source_data = ThreadSafeIter(iterable)

    for t in range(total_threads):
        thread = threading.Thread(target=worker, args=(job_queue, source_data))
        running_threads.append(thread)
        thread.start()
        logger.debug('Spawned worker thread %s' % thread)

    while True:
        item = job_queue.get()
        if item is None:
            total_threads -= 1
            logger.debug('Worker thread terminated. %s remaining.' % total_threads)

            if total_threads == 0:
                return
            else:
                continue
        else:
            yield item


def precondition(precond):
    """
    Runs the callable responsible for making some assertions
    about the data structure expected for the transformation.

    If the precondition is not achieved, a UnmetPrecondition
    exception must be raised, and then the transformation pipe
    is bypassed.
    """
    def decorator(f):
        """`f` can be a reference to a method or function. In
        both cases the `data` is expected to be passed as the
        first positional argument (obviously respecting the
        `self` argument when it is a method).
        """
        def decorated(*args):
            if len(args) > 2:
                raise TypeError('%s takes only 1 argument (or 2 for instance methods)' % f.__name__)

            try:
                instance, data = args
                if not isinstance(instance, Pipe):
                    raise TypeError('%s is not a valid pipe instance' % instance)

            except ValueError:  # tuple unpacking error
                data = args[0]

            try:
                precond(data)
            except UnmetPrecondition:
                # bypass the pipe
                return data
            else:
                return f(*args)
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

    def feed(self, iterable):
        """
        Feeds the pipe with data.

        :param iterable: the data to be processed
        """
        self._iterable_data = iterable

    def __iter__(self):
        """
        Iters through all items of ``self._iterable_data``, yielding its
        data already transformed.

        The iterable interface is the heart of the pipeline machinery.
        """
        for data in getattr(self, '_iterable_data', []):
            yield self.transform(data)

    @abc.abstractmethod
    def transform(self, data):
        """
        Performs the desired transformation to the data.
        """


class FunctionBasedPipe(Pipe):
    """
    Wraps a function to make possible its usage as a Pipe.
    """
    def __init__(self, pipe_func):
        self.declared_function = pipe_func

    def transform(self, data):
        return self.declared_function(data)


class Pipeline(object):
    """
    Represents a chain of pipes (duh).

    Accepts an arbitrary number of pipes that will be executed sequentially
    in order to transform the input data.

    :param prefetch_callable: (optional) keyword-only argument who
    receives a callable that handles data prefetching. Default is
    `thread_based_prefetch`.
    """
    def __init__(self, *args, **kwargs):
        self._pipes = []

        for pipe in args:
            # the regular case where Pipe instances are passed in
            if isinstance(pipe, Pipe):
                self._pipes.append(pipe)

            # callables may be passed if they have been properly
            # decorated with `pipe`.
            elif callable(pipe):
                try:
                    self._pipes.append(pipe._pipe)
                except AttributeError:
                    raise TypeError('%s is not a valid pipe' % pipe.__name__)
            else:
                raise TypeError('%s is not a valid pipe' % pipe.__name__)

        # the old way to handle keyword-only args
        prefetch_callable = kwargs.pop('prefetch_callable', None)
        if prefetch_callable:
            self._prefetch_callable = prefetch_callable
        else:
            self._prefetch_callable = thread_based_prefetch

    def run(self, data, rewrap=False, prefetch=0):
        """
        Wires the pipeline and returns a lazy object of
        the transformed data.

        :param data: must be an iterable, where a full document
        must be returned for each loop

        :param rewrap: (optional) is a bool that indicates the need to rewrap
        data in cases where iterating over it produces undesired results,
        for instance ``dict`` instances.

        :param prefetch: (optional) is an int defining the number of items to
        be prefetched once the pipeline starts yielding data. The
        default prefetching mechanism is based on threads, so be
        careful with CPU-bound processing pipelines.
        """
        if rewrap:
            data = [data]

        for pipe in self._pipes:
            pipe.feed(data)
            data = pipe
        else:
            iterable = self._prefetch_callable(data, prefetch) if prefetch else data
            for out_data in iterable:
                yield out_data


def pipe(callable):
    """
    Decorator that sets any callable to be used as a pipe.

    After decorated, the original callable will have a `_pipe`
    attribute containing an instance of :class:`FunctionBasedPipe`.

    Usage:

        >>> @pipe
        ... def to_upper(data):
        ...     return data.upper()
        ...
        >>> ppl = Pipeline(to_upper)
    """
    pipe_instance = FunctionBasedPipe(callable)
    setattr(callable, '_pipe', pipe_instance)
    return callable


