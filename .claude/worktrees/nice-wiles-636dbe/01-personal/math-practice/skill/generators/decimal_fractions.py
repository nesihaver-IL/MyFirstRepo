"""
Decimal & Fractions Exercise Generator

Generates exercises for converting between decimal notation and fractions.
"""

import random
from typing import Tuple, Dict, Any, Optional
from .base_generator import BaseGenerator, Exercise, MathUtils, HebrewText


class DecimalFractionsGenerator(BaseGenerator):
    """Generate decimal-fraction conversion exercises"""

    # Common fractions to decimals mapping for 5th-6th grade
    COMMON_CONVERSIONS = [
        (1, 2, 0.5),     # 1/2 = 0.5
        (1, 4, 0.25),    # 1/4 = 0.25
        (3, 4, 0.75),    # 3/4 = 0.75
        (1, 5, 0.2),     # 1/5 = 0.2
        (2, 5, 0.4),     # 2/5 = 0.4
        (3, 5, 0.6),     # 3/5 = 0.6
        (4, 5, 0.8),     # 4/5 = 0.8
        (1, 8, 0.125),   # 1/8 = 0.125
        (3, 8, 0.375),   # 3/8 = 0.375
        (5, 8, 0.625),   # 5/8 = 0.625
        (7, 8, 0.875),   # 7/8 = 0.875
        (1, 10, 0.1),    # 1/10 = 0.1
        (3, 10, 0.3),    # 3/10 = 0.3
        (1, 3, 0.333),   # 1/3 ≈ 0.333
        (2, 3, 0.667),   # 2/3 ≈ 0.667
    ]

    def __init__(
        self,
        difficulty: str = "current",
        seed: Optional[int] = None
    ):
        super().__init__("decimal_fractions", difficulty, seed)

    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """Generate a decimal-fraction conversion exercise"""

        # Alternate between decimal to fraction and fraction to decimal
        if variant_num % 2 == 0:
            return self._generate_decimal_to_fraction(variant_num)
        else:
            return self._generate_fraction_to_decimal(variant_num)

    def _generate_decimal_to_fraction(self, variant_num: int) -> Exercise:
        """Generate decimal to fraction conversion"""
        # Use common conversions for accuracy
        num, denom, decimal = random.choice(self.COMMON_CONVERSIONS)

        # Simplify if needed
        num_simp, denom_simp = MathUtils.simplify_fraction(num, denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "conversion",
            "conversion_type": "decimal_to_fraction",
            "decimal": decimal,
            "description": f"המר עשרוני לשבר: {decimal} = ___/___"
        }

        answer = {
            "fraction": {"numerator": num_simp, "denominator": denom_simp},
            "decimal": decimal,
            "steps": [
                f"הסכום העשרוני {decimal}",
                f"כתוב כשבר: {num}/{denom}",
                f"צמצם אם צריך: {num_simp}/{denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="decimal_to_fraction",
            topic="decimal_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["decimal"],
            visual_required=False
        )

    def _generate_fraction_to_decimal(self, variant_num: int) -> Exercise:
        """Generate fraction to decimal conversion"""
        num, denom, decimal = random.choice(self.COMMON_CONVERSIONS)

        # Simplify fraction
        num_simp, denom_simp = MathUtils.simplify_fraction(num, denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "conversion",
            "conversion_type": "fraction_to_decimal",
            "fraction": {"numerator": num_simp, "denominator": denom_simp},
            "description": f"המר שבר לעשרוני: {num_simp}/{denom_simp} = ___"
        }

        # Round to 3 decimal places if repeating
        decimal_rounded = round(decimal, 3)

        answer = {
            "decimal": decimal_rounded,
            "fraction": {"numerator": num_simp, "denominator": denom_simp},
            "exact_decimal": decimal,
            "steps": [
                f"חלק את המונה בהמכנה: {num_simp} ÷ {denom_simp}",
                f"תשובה: {decimal_rounded}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="fraction_to_decimal",
            topic="decimal_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["decimal"],
            visual_required=False
        )

    def validate_exercise(self, exercise: Exercise) -> bool:
        """Validate exercise correctness"""
        try:
            if exercise.exercise_type == "decimal_to_fraction":
                fraction = exercise.answer.get("fraction")
                decimal = exercise.question.get("decimal")

                if fraction and decimal:
                    computed_decimal = fraction["numerator"] / fraction["denominator"]
                    # Allow small rounding error
                    return abs(computed_decimal - decimal) < 0.01

            elif exercise.exercise_type == "fraction_to_decimal":
                fraction = exercise.question.get("fraction")
                decimal = exercise.answer.get("decimal")

                if fraction and decimal:
                    computed_decimal = fraction["numerator"] / fraction["denominator"]
                    # Allow small rounding error
                    return abs(computed_decimal - decimal) < 0.01

            return False
        except Exception:
            return False
