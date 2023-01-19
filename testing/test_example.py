import unittest
from fractions import Fraction
from example import sum

# Basic pattern is to define inputs, run the code then assert the outcomes
class TestSum(unittest.TestCase):
    def test_list_int(self):
        """Test that it can sum a list of integers
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

    def test_list_fraction(self):
        """Test that it can add sum of fractions
        """
        data = [Fraction(1,4), Fraction(1,4), Fraction(2,5)]
        result = sum(data)
        self.assertNotEqual(result, 1)
        self.assertEqual(result, Fraction(9, 10))

    def test_bad_type(self):
        """Test that it raises the correct exception
        """
        data = "banana"
        with self.assertRaises(TypeError):
            result = sum(data)


if __name__ == "__main__":
    unittest.main()
