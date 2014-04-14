# coding: utf-8
import unittest

import mocker


class PipeTests(mocker.MockerTestCase):

    def _makeOne(self, *args, **kwargs):
        from plumber import Pipe
        return Pipe(*args, **kwargs)

    def test_pipe_cannot_be_instantiated(self):
        data = {
                    'abstract_keyword_languages': None,
                    'acronym': 'AISS',
                }

        self.assertRaises(TypeError, lambda: self._makeOne(data))

    def test_returns_an_iterator(self):
        from plumber import Pipe

        class Blitz(Pipe):
            def transform(self, data):
                return 'Foo'

        data = {
                    'abstract_keyword_languages': None,
                    'acronym': 'AISS',
                }

        p = Blitz()
        p.feed(data)
        self.assertTrue(hasattr(iter(p), 'next'))

    def test_accepts_generator_objects(self):
        from plumber import Pipe

        class Blitz(Pipe):
            def transform(self, data):
                return 'Foo'

        def make_generator():
            data = {
                        'abstract_keyword_languages': None,
                        'acronym': 'AISS',
                    }
            yield data

        p = Blitz()
        p.feed(make_generator())
        self.assertTrue(hasattr(iter(p), 'next'))

    def test_passing_precondition(self):
        from plumber import Pipe, precondition
        precond = self.mocker.mock()

        precond(mocker.ANY)
        self.mocker.result(None)

        self.mocker.replay()

        class Blitz(Pipe):
            @precondition(precond)
            def transform(self, data):
                return {
                    'abstract_keyword_languages': None,
                    'acronym': 'AISS',
                }

        data = [
            {
                'abstract_keyword_languages': None,
                'acronym': 'AISS',
            },
        ]

        p = Blitz()
        p.feed(data)
        self.assertEqual(iter(p).next(), data[0])

    def test_not_passing_precondition(self):
        from plumber import Pipe, precondition, UnmetPrecondition
        precond = self.mocker.mock()

        precond(mocker.ANY)
        self.mocker.throw(UnmetPrecondition)

        self.mocker.replay()

        class Blitz(Pipe):
            @precondition(precond)
            def transform(self, data):
                """
                This transformation is not called
                """

        data = [
            {
                'abstract_keyword_languages': None,
                'acronym': 'AISS',
            },
        ]

        p = Blitz()
        p.feed(data)
        self.assertEqual(iter(p).next(), data[0])

    def test_pipes_receiving_arguments_during_initialization(self):
        from plumber import Pipe
        class Blitz(Pipe):
            def __init__(self, func):
                self.func = func

            def transform(self, data):
                """
                This transformation is not called
                """
                return self.func(data)

        data = [
            'abstract_keyword_languages',
            'acronym',
        ]

        p = Blitz(len)
        p.feed(data)

        for dt in p:
            self.assertIsInstance(dt, int)


class PipelineTests(mocker.MockerTestCase):

    def _makeOneA(self):
        from plumber import Pipe

        class A(Pipe):
            def transform(self, data):
                data['name'] = data['name'].strip()
                return data

        return A

    def _makeOneB(self):
        from plumber import Pipe

        class B(Pipe):
            def transform(self, data):
                data['name'] = data['name'].upper()
                return data

        return B

    def test_run_pipeline(self):
        from plumber import Pipeline
        A = self._makeOneA()
        B = self._makeOneB()

        ppl = Pipeline(A(), B())
        post_data = ppl.run([{'name': '  foo    '}])

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO'})

    def test_run_pipeline_prefetching_data(self):
        from plumber import Pipeline
        A = self._makeOneA()
        B = self._makeOneB()

        ppl = Pipeline(A(), B())
        post_data = ppl.run([{'name': '  foo    '}], prefetch=5)

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO'})

    def test_run_pipeline_for_rewrapped_data(self):
        from plumber import Pipeline
        A = self._makeOneA()
        B = self._makeOneB()

        ppl = Pipeline(A(), B())
        post_data = ppl.run({'name': '  foo    '}, rewrap=True)

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO'})

    def test_pipes_are_run_in_right_order(self):
        from plumber import Pipeline, Pipe
        a = self.mocker.mock(Pipe)
        b = self.mocker.mock(Pipe)

        with self.mocker.order():
            a.feed(mocker.ANY)
            self.mocker.result(a)

            b.feed(mocker.ANY)
            self.mocker.result(b)

            iter(b)
            self.mocker.result(b)

        self.mocker.replay()

        ppl = Pipeline(a, b)
        post_data = ppl.run([{'name': None}])  # placebo input value

        for pd in post_data:
            self.assertNone(pd)

    def test_prefetch_callable_is_called_when_prefetch_arg_is_greater_than_zero(self):
        raw_data = [{'name': '  foo    '}]
        pos_data = [{'name': 'FOO'}]

        pf_callable = self.mocker.mock()
        pf_callable(mocker.ANY, 5)
        self.mocker.result(pos_data)
        self.mocker.replay()

        from plumber import Pipeline
        A = self._makeOneA()
        B = self._makeOneB()

        ppl = Pipeline(A(), B(), prefetch_callable=pf_callable)
        post_data = ppl.run(raw_data, prefetch=5)

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO'})

    def test_prefetching_generators(self):
        from plumber import Pipeline
        import time
        def makeA():
            from plumber import Pipe

            class A(Pipe):
                def transform(self, data):
                    data['name'] = data['name'].strip()
                    time.sleep(0.3)
                    return data

            return A

        def makeB():
            from plumber import Pipe

            class B(Pipe):
                def transform(self, data):
                    data['name'] = data['name'].upper()
                    return data

            return B

        raw_data = ({'name': '  foo    '} for i in range(10))

        A = makeA()
        B = makeB()

        ppl = Pipeline(A(), B())

        self.assertTrue(hasattr(raw_data, 'next'))

        post_data = ppl.run(raw_data, prefetch=2)

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO'})

    def test_processing_custom_objects(self):
        class Foo(object):
            def __init__(self):
                self.name = u'Foo name'

        raw_data = Foo()
        pos_data = [{'name': 'FOO NAME'}]

        from plumber import Pipeline, Pipe
        class A(Pipe):
            def transform(self, data):
                return {'name': data.name}

        class B(Pipe):
            def transform(self, data):
                data = {k:v.upper() for k, v in data.items()}
                return data

        ppl = Pipeline(A(), B())
        post_data = ppl.run(raw_data, rewrap=True)

        for pd in post_data:
            self.assertEqual(pd, {'name': 'FOO NAME'})


class FunctionBasedPipesTests(unittest.TestCase):

    def test_pipe_decorator_adds_pipe_attribute(self):
        from plumber import pipe
        @pipe
        def do_something(data):
            return data.lower()

        self.assertTrue(hasattr(do_something, '_pipe'))

    def test_pipe_function_runs(self):
        from plumber import Pipeline, pipe
        @pipe
        def do_something(data):
            return data.lower()

        ppl = Pipeline(do_something)
        post_data = ppl.run(['FOO'])

        self.assertEqual(next(post_data), 'foo')

    def test_non_decorated_functions_fails(self):
        from plumber import Pipeline
        def do_something(data):
            return data.lower()

        self.assertRaises(ValueError, lambda: Pipeline(do_something))

