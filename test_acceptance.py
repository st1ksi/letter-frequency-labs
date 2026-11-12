"""Перевірки того, що приймальний набір справді знаходить розбіжності."""
import unittest
from acceptance import compare, load_cases


class AcceptanceRunnerTests(unittest.TestCase):
    def test_coverage_includes_required_variant_cases(self):
        cases = load_cases()['cases']
        self.assertGreaterEqual(len(cases), 6)
        self.assertTrue({'empty-text', 'one-letter', 'no-letters', 'empty-file'} <= {c['id'] for c in cases})

    def test_comparison_checks_each_channel_and_exit_status(self):
        expected = {'stdout': 'вихід\n', 'stderr': '', 'exit_code': 0}
        self.assertTrue(compare(dict(expected), expected))
        for key, wrong in [('stdout', 'інше\n'), ('stderr', 'помилка\n'), ('exit_code', 2)]:
            with self.subTest(channel=key):
                actual = dict(expected)
                actual[key] = wrong
                self.assertFalse(compare(actual, expected))


if __name__ == '__main__':
    unittest.main()
