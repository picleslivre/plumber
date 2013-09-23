# coding: utf-8
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
        from plumber import Pipeline
        a = self.mocker.mock()
        b = self.mocker.mock()

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
