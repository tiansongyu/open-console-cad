"""Regression checks for retained CAD identities after removing false parts."""
import unittest
from cadlib.part_numbers import allocate_part_numbers


class NumberingTests(unittest.TestCase):
    def test_default_stays_sequential(self):
        self.assertEqual(allocate_part_numbers(['PSV-0032', ''], 'PSV'),
                         ['PSV-0001', 'PSV-0002'])

    def test_preserves_gaps_and_never_reuses_retired_highest_number(self):
        self.assertEqual(allocate_part_numbers(['PSV-0001', 'PSV-0010', '', ''],
                         'PSV', True, ['PSV-0002', 'PSV-0015']),
                         ['PSV-0001', 'PSV-0010', 'PSV-0016', 'PSV-0017'])

    def test_conflicting_live_or_retired_identity_fails(self):
        for existing, reserved in [(['PSV-0001', 'PSV-0001'], []),
                                   (['PSV-0001'], ['PSV-0001'])]:
            with self.assertRaises(ValueError):
                allocate_part_numbers(existing, 'PSV', True, reserved)

    def test_wrong_device_number_fails(self):
        with self.assertRaises(ValueError):
            allocate_part_numbers(['PSP-0001'], 'PSV', True)


if __name__ == '__main__':
    unittest.main()
