"""Sweden can be chosen without a US state map."""
import unittest

from engine.setup.regions import country


class Regions(unittest.TestCase):
    def test_sweden(self):
        self.assertEqual(country('SE')['title'], 'Sweden')
        self.assertIsNone(country('CA'))


if __name__ == '__main__':
    unittest.main()
