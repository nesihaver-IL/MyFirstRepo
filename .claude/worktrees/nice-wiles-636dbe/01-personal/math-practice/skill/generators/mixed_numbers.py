"""
Mixed Numbers & Improper Fractions Exercise Generator

Generates exercises for converting between mixed numbers and improper fractions.
"""

import random
from typing import Tuple, Dict, Any, Optional
from .base_generator import BaseGenerator, Exercise, MathUtils, HebrewText


class MixedNumbersGenerator(BaseGenerator):
    """Generate mixed numbers and improper fractions exercises"""

    def __init__(
        self,
        difficulty: str = "current",
        seed: Optional[int] = None,
        whole_range: Tuple[int, int] = (1, 5),
        numerator_range: Tuple[int, int] = (1, 9),
        denominator_range: Tuple[int, int] = (2, 10)
    ):
        super().__init__("mixed_improper_fractions", difficulty, seed)
        self.whole_range = whole_range
        self.numerator_range = numerator_range
        self.denominator_range = denominator_range

    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """Generate a mixed number conversion exercise"""

        # Alternate between improper to mixed and mixed to improper
        if variant_num % 2 == 0:
            return self._generate_improper_to_mixed(variant_num)
        else:
            return self._generate_mixed_to_improper(variant_num)

    def _generate_improper_to_mixed(self, variant_num: int) -> Exercise:
        """Generate improper fraction to mixed number conversion"""
        denom = random.randint(*self.denominator_range)
        whole = random.randint(*self.whole_range)
        numerator = random.randint(1, denom - 1)

        # Create improper fraction: whole * denom + numerator
        improper_num = whole * denom + numerator

        # Result is mixed number
        result_whole = improper_num // denom
        result_num = improper_num % denom

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "conversion",
            "conversion_type": "improper_to_mixed",
            "improper_fraction": {"numerator": improper_num, "denominator": denom},
            "description": f"המר: {improper_num}/{denom} = ___ ___/___"
        }

        answer = {
            "mixed_number": {
                "whole": result_whole,
                "numerator": result_num,
                "denominator": denom
            },
            "steps": [
                f"חלק את המונה בהמכנה: {improper_num} ÷ {denom}",
                f"תוצאה שלמה: {result_whole}, שארית: {result_num}",
                f"תשובה: {result_whole} {result_num}/{denom}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="improper_to_mixed",
            topic="mixed_improper_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["convert_mixed"],
            visual_required=True
        )

    def _generate_mixed_to_improper(self, variant_num: int) -> Exercise:
        """Generate mixed number to improper fraction conversion"""
        whole, num, denom = self.randomize_whole_and_fraction(
            self.whole_range,
            self.numerator_range,
            self.denominator_range
        )

        # Result improper fraction
        improper_num = whole * denom + num

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "conversion",
            "conversion_type": "mixed_to_improper",
            "mixed_number": {
                "whole": whole,
                "numerator": num,
                "denominator": denom
            },
            "description": f"המר: {whole} {num}/{denom} = ___/___"
        }

        answer = {
            "improper_fraction": {
                "numerator": improper_num,
                "denominator": denom
            },
            "steps": [
                f"כפול את השלם בהמכנה: {whole} × {denom} = {whole * denom}",
                f"הוסף את המונה: {whole * denom} + {num} = {improper_num}",
                f"תשובה: {improper_num}/{denom}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="mixed_to_improper",
            topic="mixed_improper_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["convert_mixed"],
            visual_required=True
        )

    def validate_exercise(self, exercise: Exercise) -> bool:
        """Validate exercise correctness"""
        try:
            exercise_type = exercise.exercise_type

            if exercise_type == "improper_to_mixed":
                improper = exercise.question["improper_fraction"]
                mixed = exercise.answer["mixed_number"]

                # Verify conversion
                original_value = improper["numerator"]
                computed_value = mixed["whole"] * mixed["denominator"] + mixed["numerator"]

                return original_value == computed_value

            elif exercise_type == "mixed_to_improper":
                mixed = exercise.question["mixed_number"]
                improper = exercise.answer["improper_fraction"]

                # Verify conversion
                computed_improper = mixed["whole"] * mixed["denominator"] + mixed["numerator"]

                return computed_improper == improper["numerator"]

            return False
        except Exception:
            return False
