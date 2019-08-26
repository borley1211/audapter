# -*- coding: utf-8 -*-
import unittest

import adaptune


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_passalsa_main_at_time(self):
        domain = 'time'
        expected = True
        actual = adaptune.passalsa.main(domain=domain, run_time=30)
        self.assertEqual(expected, actual)
