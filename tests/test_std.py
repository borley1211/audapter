# -*- coding: utf-8 -*-
import unittest

import adaptune


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_monitor(self):
        runtime = 2
        devname = adaptune.dev["monitor"]
        expected = None
        actual = adaptune.monitor(device=devname, run_time=runtime)
        self.assertEqual(expected, actual)
