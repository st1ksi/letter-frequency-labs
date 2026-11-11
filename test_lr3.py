import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from main import main, render_histogram
from scaling import scale_bars
from vendor.zanalyze_histogram import print_histogram


class ScalingBoundaryTests(unittest.TestCase):
    def test_prerecorded_boundaries(self):
        cases = json.loads((Path(__file__).parent / 'docs/expected-cases.json').read_text(encoding='utf-8'))
        for values, width, expected in cases:
            with self.subTest(values=str(values)[:80], width=width):
                if expected == 'ValueError':
                    with self.assertRaises(ValueError):
                        scale_bars(values, width)
                else:
                    self.assertEqual(scale_bars(values, width), expected)

    def test_halfway_rounds_up_in_application(self):
        self.assertIn('б ' + '#' * 3 + ' 5', render_histogram({'а': 100, 'б': 5}).splitlines())

    def test_generated_input_is_unchanged(self):
        values = [0, 5, 100]
        scale_bars(values)
        self.assertEqual(values, [0, 5, 100])


class ThirdPartyTests(unittest.TestCase):
    def test_console_renderer_handles_pairs(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_histogram('Example', [('a', 4), ('b', 2)], 6, 'Letter', width=50)
        self.assertIn('█' * 50, output.getvalue())
        self.assertIn('█' * 25, output.getvalue())
        self.assertIn('66.67%', output.getvalue())

    def test_all_zero_rows(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_histogram('Zero', [('a', 0), ('b', 0)], 0, 'Letter')
        self.assertNotIn('█', output.getvalue())
        self.assertEqual(output.getvalue().count('0.00%'), 2)

    def test_real_call_is_required_for_blocks(self):
        with patch('main.print_histogram', side_effect=RuntimeError('dependency called')):
            with self.assertRaisesRegex(RuntimeError, 'dependency called'):
                render_histogram({'а': 4, 'б': 2}, 1, 'blocks')

    def test_blocks_cli_preserves_filtered_totals(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch('builtins.input', return_value='ааааббв'), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(main(['--chart-style', 'blocks', '--min-count', '2']), 0)
        result = output.getvalue()
        self.assertIn('zanalyze', result)
        self.assertIn('█' * 50, result)
        self.assertIn('Усього літер: 7; різних: 3', result)
        self.assertIn('Показано різних літер: 2; поріг: 2.', result)
        self.assertEqual(errors.getvalue(), '')

    def test_unknown_cli_style_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(['--chart-style', 'unknown'])
        self.assertEqual(error.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
