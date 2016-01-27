import os
import unittest
from render_math import parse_tex_macros, _parse_macro, _filter_duplicates

class TestParseMacros(unittest.TestCase):
    def test_multiple_arguments(self):
        """Parse a definition with multiple arguments"""
        text = r'\newcommand{\pp}[2]{\frac{ #1}{ #2} \cdot 2}'
        line = {'filename': '/home/user/example.tex', 'line_num': 1, 'def':
            text}
        parsed = _parse_macro(line)
        expected = {'name':'pp',
                     'definition': '\\\\\\\\frac{ #1}{ #2} \\\\\\\\cdot 2',
                     'args': '2',
                    'line': 1,
                    'file': '/home/user/example.tex'}
        self.assertEqual(parsed, expected)

    def test_no_arguments(self):
        """Parse a definition without arguments"""
        text = r'\newcommand{\circ}{2 \pi R}'
        line = {'filename': '/home/user/example.tex', 'line_num': 1, 'def':
            text}
        parsed = _parse_macro(line)
        expected = {'name':'circ',
                     'definition': '2 \\\\\\\\pi R',
                    'line': 1,
                    'file': '/home/user/example.tex'
                     }
        self.assertEqual(parsed, expected)

    def test_repeated_definitions_same_file(self):
        """Last definition is used"""
        text1 = r'2 \\\\\\\\pi R'
        text2 = r'2 \\\\\\\\pi r'
        common_file = '/home/user/example.tex'
        def1 = {'name': 'circ', 'line': 1, 'definition': text1,
                 'file': common_file}
        def2 = {'name': 'circ', 'line': 2, 'definition': text2,
                 'file': common_file}
        expected = [{'name':'circ',
                     'definition': r'2 \\\\\\\\pi r',
                     'line': 2,
                     'file': '/home/user/example.tex'
                     }]
        parsed = _filter_duplicates(def1, def2)
        self.assertEqual(parsed, expected)

    def test_repeated_definitions_different_files(self):
        """Last definition is used"""
        text1 = r'2 \\\\\\\\pi R'
        text2 = r'2 \\\\\\\\pi r'
        file1 = '/home/user/example1.tex'
        file2 = '/home/user/example2.tex'
        def1 = {'name': 'circ', 'line': 1, 'definition': text1,
                 'file': file1}
        def2 = {'name': 'circ', 'line': 1, 'definition': text2,
                 'file': file2}
        expected = [{'name':'circ',
                     'definition': r'2 \\\\\\\\pi r',
                     'line': 1,
                     'file': '/home/user/example2.tex'
                     }]
        parsed = _filter_duplicates(def1, def2)
        self.assertEqual(parsed, expected)

    def test_load_file(self):
        cur_dir = os.path.split(os.path.realpath(__file__))[0]
        test_fname = os.path.join(cur_dir, "latex-commands-example.tex")
        parsed = parse_tex_macros([test_fname])
        expected = [{'name': 'pp',
                     'definition': '\\\\\\\\frac{\\\\\\\\partial #1}{'
                                   '\\\\\\\\partial #2}',
                     'args': '2'},
                    {'name': 'bb',
                     'definition': '\\\\\\\\pi R',},
                    {'name': 'bc',
                     'definition': '\\\\\\\\pi r',
                     }]
        self.maxDiff = None
        self.assertEqual(parsed, expected)

if __name__ == '__main__':
    unittest.main()