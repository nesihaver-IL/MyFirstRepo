"""
Unit Tests for Exercise Generators

Validates exercise generation, simplification, and conversion logic.
"""

import sys
sys.path.insert(0, "/home/nhaver/MyFirstRepo/01-personal/math-practice")

import unittest
from skill.generators.base_generator import MathUtils, HebrewText
from skill.generators.fraction_comparison import FractionComparisonGenerator
from skill.generators.fraction_operations import FractionOperationsGenerator
from skill.generators.mixed_numbers import MixedNumbersGenerator
from skill.generators.visual_fractions import VisualFractionsGenerator
from skill.generators.decimal_fractions import DecimalFractionsGenerator


class TestMathUtils(unittest.TestCase):
    """Test mathematical utility functions"""

    def test_gcd(self):
        """Test greatest common divisor"""
        self.assertEqual(MathUtils.gcd(12, 8), 4)
        self.assertEqual(MathUtils.gcd(17, 13), 1)
        self.assertEqual(MathUtils.gcd(100, 50), 50)

    def test_lcm(self):
        """Test least common multiple"""
        self.assertEqual(MathUtils.lcm(4, 6), 12)
        self.assertEqual(MathUtils.lcm(3, 5), 15)
        self.assertEqual(MathUtils.lcm(12, 8), 24)

    def test_simplify_fraction(self):
        """Test fraction simplification"""
        self.assertEqual(MathUtils.simplify_fraction(4, 8), (1, 2))
        self.assertEqual(MathUtils.simplify_fraction(6, 9), (2, 3))
        self.assertEqual(MathUtils.simplify_fraction(7, 1), (7, 1))
        self.assertEqual(MathUtils.simplify_fraction(0, 5), (0, 1))

    def test_is_equivalent(self):
        """Test fraction equivalence"""
        self.assertTrue(MathUtils.is_equivalent(1, 2, 2, 4))
        self.assertTrue(MathUtils.is_equivalent(1, 2, 3, 6))
        self.assertFalse(MathUtils.is_equivalent(1, 2, 1, 3))

    def test_compare_fractions(self):
        """Test fraction comparison"""
        self.assertEqual(MathUtils.compare_fractions(1, 2, 2, 3), -1)  # 1/2 < 2/3
        self.assertEqual(MathUtils.compare_fractions(3, 4, 2, 4), 1)   # 3/4 > 2/4
        self.assertEqual(MathUtils.compare_fractions(1, 2, 2, 4), 0)   # 1/2 = 2/4

    def test_improper_to_mixed(self):
        """Test improper to mixed conversion"""
        self.assertEqual(MathUtils.improper_to_mixed(7, 4), (1, 3, 4))
        self.assertEqual(MathUtils.improper_to_mixed(11, 5), (2, 1, 5))
        self.assertEqual(MathUtils.improper_to_mixed(5, 2), (2, 1, 2))

    def test_mixed_to_improper(self):
        """Test mixed to improper conversion"""
        self.assertEqual(MathUtils.mixed_to_improper(1, 3, 4), (7, 4))
        self.assertEqual(MathUtils.mixed_to_improper(2, 1, 5), (11, 5))
        self.assertEqual(MathUtils.mixed_to_improper(0, 3, 4), (3, 4))


class TestFractionComparisonGenerator(unittest.TestCase):
    """Test fraction comparison exercise generation"""

    def setUp(self):
        self.generator = FractionComparisonGenerator(difficulty="current", seed=42)

    def test_generate_exercise(self):
        """Test exercise generation"""
        exercise = self.generator.generate_exercise(0)
        self.assertIsNotNone(exercise)
        self.assertEqual(exercise.topic, "fraction_comparison")

    def test_exercise_validation(self):
        """Test exercise validation"""
        exercise = self.generator.generate_exercise(0)
        self.assertTrue(self.generator.validate_exercise(exercise))

    def test_operator_in_answer(self):
        """Test that operator is valid"""
        for i in range(10):
            exercise = self.generator.generate_exercise(i)
            operator = exercise.answer.get("operator")
            self.assertIn(operator, [">", "<", "="])


class TestFractionOperationsGenerator(unittest.TestCase):
    """Test fraction operations exercise generation"""

    def setUp(self):
        self.generator_current = FractionOperationsGenerator(difficulty="current", seed=42)
        self.generator_advanced = FractionOperationsGenerator(difficulty="advanced", seed=42)

    def test_generate_addition(self):
        """Test addition exercise generation"""
        exercise = self.generator_current.generate_exercise(0)
        self.assertIsNotNone(exercise.answer.get("result"))
        self.assertTrue(exercise.answer["result"]["denominator"] > 0)

    def test_result_validation(self):
        """Test that results are simplified correctly"""
        for i in range(10):
            exercise = self.generator_current.generate_exercise(i)
            self.assertTrue(self.generator_current.validate_exercise(exercise))

    def test_advanced_difficulty(self):
        """Test advanced exercises exist"""
        exercise = self.generator_advanced.generate_exercise(0)
        self.assertEqual(exercise.difficulty, "advanced")


class TestMixedNumbersGenerator(unittest.TestCase):
    """Test mixed numbers exercise generation"""

    def setUp(self):
        self.generator = MixedNumbersGenerator(difficulty="current", seed=42)

    def test_improper_to_mixed(self):
        """Test improper to mixed conversion exercise"""
        exercise = self.generator._generate_improper_to_mixed(0)
        self.assertEqual(exercise.exercise_type, "improper_to_mixed")

    def test_mixed_to_improper(self):
        """Test mixed to improper conversion exercise"""
        exercise = self.generator._generate_mixed_to_improper(1)
        self.assertEqual(exercise.exercise_type, "mixed_to_improper")

    def test_conversion_correctness(self):
        """Test conversion is mathematically correct"""
        exercise = self.generator._generate_improper_to_mixed(0)
        mixed = exercise.answer["mixed_number"]
        original = exercise.question["improper_fraction"]

        # Verify: improper_num = whole * denom + numerator
        computed = mixed["whole"] * mixed["denominator"] + mixed["numerator"]
        self.assertEqual(computed, original["numerator"])


class TestVisualFractionsGenerator(unittest.TestCase):
    """Test visual fractions exercise generation"""

    def setUp(self):
        self.generator = VisualFractionsGenerator(difficulty="current", seed=42)

    def test_generate_visual_exercise(self):
        """Test visual exercise generation"""
        exercise = self.generator.generate_exercise(0)
        self.assertTrue(exercise.visual_required)

    def test_grid_shading(self):
        """Test grid shading exercise"""
        exercise = self.generator._generate_grid_shading(0)
        self.assertEqual(exercise.exercise_type, "grid_shading")

    def test_pie_chart(self):
        """Test pie chart exercise"""
        exercise = self.generator._generate_pie_chart(0)
        self.assertIn(exercise.exercise_type, ["pie_identify", "pie_color"])


class TestDecimalFractionsGenerator(unittest.TestCase):
    """Test decimal-fraction conversion exercises"""

    def setUp(self):
        self.generator = DecimalFractionsGenerator(seed=42)

    def test_decimal_to_fraction(self):
        """Test decimal to fraction conversion"""
        exercise = self.generator._generate_decimal_to_fraction(0)
        self.assertEqual(exercise.exercise_type, "decimal_to_fraction")

    def test_fraction_to_decimal(self):
        """Test fraction to decimal conversion"""
        exercise = self.generator._generate_fraction_to_decimal(1)
        self.assertEqual(exercise.exercise_type, "fraction_to_decimal")

    def test_conversion_accuracy(self):
        """Test conversion accuracy"""
        for i in range(10):
            exercise = self.generator.generate_exercise(i)
            self.assertTrue(self.generator.validate_exercise(exercise))


class TestHebrewText(unittest.TestCase):
    """Test Hebrew text generation"""

    def test_instructions_exist(self):
        """Test that Hebrew instructions exist"""
        self.assertIsNotNone(HebrewText.INSTRUCTIONS.get("compare"))
        self.assertIsNotNone(HebrewText.INSTRUCTIONS.get("simplify"))

    def test_hebrew_fraction_format(self):
        """Test Hebrew fraction formatting"""
        result = HebrewText.hebrew_fraction(3, 4)
        self.assertEqual(result, "3/4")


def run_tests():
    """Run all tests and report results"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
