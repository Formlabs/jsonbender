import unittest

from jsonbender import S, K
from jsonbender.core import bend, BendingException, Context
from jsonbender.test import BenderTestMixin


class TestBend(unittest.TestCase):
    def test_empty_mapping(self):
        self.assertDictEqual(bend({}, {'a': 1}), {})

    def test_flat_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'another_field': K('wow'),
        }
        source = {'a': {'b': 'ok'}}
        expected = {
            'a_field': 'ok',
            'another_field': 'wow',
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': {
                'nested': {
                    'field': S('f1', 'f2'),
                },
            },
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': {'nested': {'field': 'hi'}},
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_nested_mapping_with_lists(self):
        mapping = {
            'a_field': S('a', 'b'),
            'a': [{
                'nested': {
                    'field': S('f1', 'f2'),
                },
            }],
        }
        source = {
            'a': {'b': 'ok'},
            'f1': {'f2': 'hi'},
        }
        expected = {
            'a_field': 'ok',
            'a': [{'nested': {'field': 'hi'}}],
        }
        self.assertDictEqual(bend(mapping, source), expected)

    def test_bending_exception_is_raised_when_something_bad_happens(self):
        mapping = {'a': S('nonexistant')}
        source = {}
        self.assertRaises(BendingException, bend, mapping, source)

    def test_constants_without_K(self):
        mapping = {'a': 'a const value', 'b': 123}
        self.assertDictEqual(bend(mapping, {}),
                             {'a': 'a const value', 'b': 123})

    def test_context_shallow(self):
        mapping = {'a': Context() >> S('b')}
        res = bend(mapping, {}, context={'b': 23})
        self.assertDictEqual(res, {'a': 23})

    def test_context_deep(self):
        mapping = {'a': [{'a': Context() >> S('b')}]}
        res = bend(mapping, {}, context={'b': 23})
        self.assertDictEqual(res, {'a': [{'a': 23}]})


class TestOperators(unittest.TestCase, BenderTestMixin):
    def test_add(self):
        self.assert_bender(K(5) + K(2), None, 7)

    def test_sub(self):
        self.assert_bender(K(5) - K(2), None, 3)

    def test_mul(self):
        self.assert_bender(K(5) * K(2), None, 10)

    def test_div(self):
        self.assert_bender(K(4) / K(2), None, 2)
        self.assertAlmostEqual((K(5) / K(2))(None), 2.5, 2)


class TestGetItem(unittest.TestCase, BenderTestMixin):
    def test_getitem(self):
        bender = S('val')[2:8:2]
        self.assert_bender(bender, {'val': range(10)}, [2, 4, 6])


if __name__ == '__main__':
    unittest.main()
