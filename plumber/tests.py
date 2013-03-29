# coding: utf-8
import mocker


class PipeTests(mocker.MockerTestCase):

    def _makeOne(self, *args, **kwargs):
        from plumber.base import Pipe
        return Pipe(*args, **kwargs)

    def test_pipe_cannot_be_instantiated(self):
        data = {
                    'abstract_keyword_languages': None,
                    'acronym': 'AISS',
                }

        self.assertRaises(TypeError, lambda: self._makeOne(data))

    def test_returns_an_iterator(self):
        from plumber.base import Pipe

        class Blitz(Pipe):
            def transform(self, data):
                return 'Foo'

        data = {
                    'abstract_keyword_languages': None,
                    'acronym': 'AISS',
                }

        p = Blitz(data)
        self.assertTrue(hasattr(iter(p), 'next'))

    def test_accepts_generator_objects(self):
        from plumber.base import Pipe

        class Blitz(Pipe):
            def transform(self, data):
                return 'Foo'

        def make_generator():
            data = {
                        'abstract_keyword_languages': None,
                        'acronym': 'AISS',
                    }
            yield data

        p = Blitz(make_generator())
        self.assertTrue(hasattr(iter(p), 'next'))

    def test_passing_precondition(self):
        from plumber.base import Pipe, precondition
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

        p = Blitz(data)
        self.assertEqual(iter(p).next(), data[0])

    def test_not_passing_precondition(self):
        from plumber.base import Pipe, precondition, UnmetPrecondition
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

        p = Blitz(data)
        self.assertEqual(iter(p).next(), data[0])
