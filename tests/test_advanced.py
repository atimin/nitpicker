# -*- coding: utf-8 -*-

from .context import nitpicker

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        self.assertIsNone(nitpicker.hmm())


if __name__ == '__main__':
    unittest.main()
