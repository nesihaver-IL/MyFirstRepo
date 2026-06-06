"""
Fraction Comparison Exercise Generator

Generates exercises for comparing fractions using >, <, = operators.
Supports same denominator, different denominators, and mixed integer comparisons.
"""

import random
from typing import Tuple, Dict, Any, Optional
from .base_generator import BaseGenerator, Exercise, MathUtils, HebrewText


class FractionComparisonGenerator(BaseGenerator):
    """Generate fraction comparison exercises"""

    OPERATORS = [">", "<", "="]

    def __init__(
        self,
        difficulty: str = "current",
        seed: Optional[int] = None,
        numerator_range: Tuple[int, int] = (1, 10),
        denominator_range: Tuple[int, int] = (2, 12)
    ):
        super().__init__("fraction_comparison", difficulty, seed)
        self.numerator_range = numerator_range
        self.denominator_range = denominator_range

    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """Generate a fraction comparison exercise"""

        # Pick comparison type
        comparison_type = random.choice(["same_denom", "different_denom", "with_integer"])

        if comparison_type == "same_denom":
            return self._generate_same_denominator(variant_num)
        elif comparison_type == "different_denom":
            return self._generate_different_denominator(variant_num)
        else:
            return self._generate_with_integer(variant_num)

    def _generate_same_denominator(self, variant_num: int) -> Exercise:
        """Generate comparison with same denominator"""
        denom = random.randint(*self.denominator_range)
        num1 = random.randint(1, denom - 1)
        num2 = random.randint(1, denom - 1)

        # Ensure different fractions
        while num1 == num2:
            num2 = random.randint(1, denom - 1)

        # Determine correct operator
        if num1 > num2:
            correct_operator = ">"
        elif num1 < num2:
            correct_operator = "<"
        else:
            correct_operator = "="

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "comparison",
            "fraction1": {"numerator": num1, "denominator": denom},
            "fraction2": {"numerator": num2, "denominator": denom},
            "description": f"{num1}/{denom} ___ {num2}/{denom}"
        }

        answer = {
            "operator": correct_operator,
            "explanation": f"מכנה זהה, לכן משווים רק את המונים: {num1} {self._operator_hebrew(correct_operator)} {num2}"
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="comparison_same_denom",
            topic="fraction_comparison",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["compare"],
            visual_required=False
        )

    def _generate_different_denominator(self, variant_num: int) -> Exercise:
        """Generate comparison with different denominators"""
        # Generate two different fractions
        num1, denom1 = self.randomize_fraction(self.numerator_range, self.denominator_range)
        num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Ensure different denominators
        while denom1 == denom2:
            num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Determine correct operator
        comparison = MathUtils.compare_fractions(num1, denom1, num2, denom2)
        if comparison > 0:
            correct_operator = ">"
        elif comparison < 0:
            correct_operator = "<"
        else:
            correct_operator = "="

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "comparison",
            "fraction1": {"numerator": num1, "denominator": denom1},
            "fraction2": {"numerator": num2, "denominator": denom2},
            "description": f"{num1}/{denom1} ___ {num2}/{denom2}"
        }

        # Calculate visual aid: common denominator
        lcm_denom = MathUtils.lcm(denom1, denom2)
        equiv1_num = num1 * (lcm_denom // denom1)
        equiv2_num = num2 * (lcm_denom // denom2)

        answer = {
            "operator": correct_operator,
            "explanation": f"המכנים שונים. המרה למכנה משותף {lcm_denom}: {equiv1_num}/{lcm_denom} {self._operator_hebrew(correct_operator)} {equiv2_num}/{lcm_denom}",
            "visual_aid": {
                "type": "grid_comparison",
                "fraction1": {"numerator": num1, "denominator": denom1},
                "fraction2": {"numerator": num2, "denominator": denom2}
            }
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="comparison_different_denom",
            topic="fraction_comparison",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["compare"],
            visual_required=True
        )

    def _generate_with_integer(self, variant_num: int) -> Exercise:
        """Generate comparison with whole numbers"""
        # Decide: fraction > 1, < 1, or = 1
        comparison_type = random.choice(["greater", "less", "equal"])

        if comparison_type == "greater":
            # Improper fraction vs integer
            num = random.randint(self.numerator_range[0], self.numerator_range[1])
            denom = random.randint(2, 8)
            whole = num // denom  # Make sure fraction > whole

            correct_operator = ">" if num % denom != 0 or num // denom > whole else "="

        elif comparison_type == "less":
            # Proper fraction vs integer
            num = random.randint(1, self.numerator_range[1])
            denom = random.randint(num + 1, self.denominator_range[1])
            whole = random.randint(1, 3)

            correct_operator = "<"

        else:  # equal
            whole = random.randint(1, 3)
            num = whole
            denom = 1
            correct_operator = "="

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "comparison_mixed",
            "fraction": {"numerator": num, "denominator": denom},
            "integer": whole,
            "description": f"{num}/{denom} ___ {whole}"
        }

        answer = {
            "operator": correct_operator,
            "explanation": f"השברשווה {num/denom:.2f}, זה {self._compare_to_whole(num, denom, whole)} מ-{whole}"
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="comparison_with_integer",
            topic="fraction_comparison",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["compare"],
            visual_required=True
        )

    def validate_exercise(self, exercise: Exercise) -> bool:
        """Validate exercise correctness"""
        try:
            operator = exercise.answer.get("operator")
            if operator not in self.OPERATORS:
                return False

            # Verify fractions are valid
            if "fraction1" in exercise.question:
                f1 = exercise.question["fraction1"]
                if f1["denominator"] == 0:
                    return False

            return True
        except Exception:
            return False

    def _operator_hebrew(self, operator: str) -> str:
        """Get Hebrew name for operator"""
        mapping = {">": "גדול מ", "<": "קטן מ", "=": "שווה ל"}
        return mapping.get(operator, operator)

    def _compare_to_whole(self, num: int, denom: int, whole: int) -> str:
        """Get Hebrew description of comparison"""
        fraction_value = num / denom
        if fraction_value > whole:
            return "גדול"
        elif fraction_value < whole:
            return "קטן"
        else:
            return "שווה"
