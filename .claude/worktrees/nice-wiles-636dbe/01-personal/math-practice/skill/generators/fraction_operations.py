"""
Fraction Operations Exercise Generator

Generates exercises for addition, subtraction, and multiplication of fractions.
Supports same denominator, different denominators (advanced), and whole number operations.
"""

import random
from typing import Tuple, Dict, Any, Optional
from .base_generator import BaseGenerator, Exercise, MathUtils, HebrewText


class FractionOperationsGenerator(BaseGenerator):
    """Generate fraction operation exercises"""

    def __init__(
        self,
        difficulty: str = "current",
        seed: Optional[int] = None,
        numerator_range: Tuple[int, int] = (1, 8),
        denominator_range: Tuple[int, int] = (2, 8)
    ):
        super().__init__("fraction_operations", difficulty, seed)
        self.numerator_range = numerator_range
        self.denominator_range = denominator_range

    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """Generate a fraction operation exercise"""

        if self.difficulty == "current":
            # 5th grade: same denominator or simple multiplication
            operation = random.choice(["addition", "subtraction", "multiplication"])
        else:
            # 6th grade (advanced): can include different denominators
            operation = random.choice(["addition", "subtraction", "multiplication", "division"])

        if operation == "addition":
            if self.difficulty == "current":
                return self._generate_addition_same_denom(variant_num)
            else:
                return self._generate_addition_different_denom(variant_num)
        elif operation == "subtraction":
            if self.difficulty == "current":
                return self._generate_subtraction_same_denom(variant_num)
            else:
                return self._generate_subtraction_different_denom(variant_num)
        elif operation == "multiplication":
            return self._generate_multiplication(variant_num)
        else:  # division
            return self._generate_division(variant_num)

    def _generate_addition_same_denom(self, variant_num: int) -> Exercise:
        """Generate addition with same denominator"""
        denom = random.randint(*self.denominator_range)
        num1 = random.randint(1, denom - 1)
        num2 = random.randint(1, denom - 1)

        # Result shouldn't be improper for current level
        while num1 + num2 > denom:
            num2 = random.randint(1, denom - num1)

        result_num = num1 + num2
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "+",
            "fraction1": {"numerator": num1, "denominator": denom},
            "fraction2": {"numerator": num2, "denominator": denom},
            "description": f"{num1}/{denom} + {num2}/{denom} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"מכנה זהה, חבר את המונים: {num1} + {num2} = {result_num}",
                f"אם צריך, צמצם: {result_num}/{denom} = {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="addition_same_denom",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def _generate_subtraction_same_denom(self, variant_num: int) -> Exercise:
        """Generate subtraction with same denominator"""
        denom = random.randint(*self.denominator_range)
        num1 = random.randint(2, denom - 1)
        num2 = random.randint(1, num1 - 1)  # num2 < num1 to avoid negative

        result_num = num1 - num2
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "-",
            "fraction1": {"numerator": num1, "denominator": denom},
            "fraction2": {"numerator": num2, "denominator": denom},
            "description": f"{num1}/{denom} - {num2}/{denom} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"מכנה זהה, חסר את המונים: {num1} - {num2} = {result_num}",
                f"אם צריך, צמצם: {result_num}/{denom} = {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="subtraction_same_denom",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def _generate_addition_different_denom(self, variant_num: int) -> Exercise:
        """Generate addition with different denominators (advanced)"""
        num1, denom1 = self.randomize_fraction(self.numerator_range, self.denominator_range)
        num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Find common denominator
        lcm_denom = MathUtils.lcm(denom1, denom2)
        equiv1_num = num1 * (lcm_denom // denom1)
        equiv2_num = num2 * (lcm_denom // denom2)

        result_num = equiv1_num + equiv2_num
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, lcm_denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "+",
            "fraction1": {"numerator": num1, "denominator": denom1},
            "fraction2": {"numerator": num2, "denominator": denom2},
            "description": f"{num1}/{denom1} + {num2}/{denom2} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"מצא מכנה משותף (ל.כ.מ): {lcm_denom}",
                f"המר: {num1}/{denom1} = {equiv1_num}/{lcm_denom}, {num2}/{denom2} = {equiv2_num}/{lcm_denom}",
                f"חבר: {equiv1_num}/{lcm_denom} + {equiv2_num}/{lcm_denom} = {result_num}/{lcm_denom}",
                f"צמצם: {result_num}/{lcm_denom} = {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="addition_different_denom",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def _generate_subtraction_different_denom(self, variant_num: int) -> Exercise:
        """Generate subtraction with different denominators (advanced)"""
        num1, denom1 = self.randomize_fraction(self.numerator_range, self.denominator_range)
        num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Find common denominator
        lcm_denom = MathUtils.lcm(denom1, denom2)
        equiv1_num = num1 * (lcm_denom // denom1)
        equiv2_num = num2 * (lcm_denom // denom2)

        # Ensure first is larger
        if equiv1_num < equiv2_num:
            equiv1_num, equiv2_num = equiv2_num, equiv1_num

        result_num = equiv1_num - equiv2_num
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, lcm_denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "-",
            "fraction1": {"numerator": num1, "denominator": denom1},
            "fraction2": {"numerator": num2, "denominator": denom2},
            "description": f"{equiv1_num}/{lcm_denom} - {equiv2_num}/{lcm_denom} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"מצא מכנה משותף (ל.כ.מ): {lcm_denom}",
                f"חסר: {equiv1_num}/{lcm_denom} - {equiv2_num}/{lcm_denom} = {result_num}/{lcm_denom}",
                f"צמצם: {result_num}/{lcm_denom} = {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="subtraction_different_denom",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def _generate_multiplication(self, variant_num: int) -> Exercise:
        """Generate multiplication of fractions"""
        # For current level: fraction × whole number
        # For advanced: fraction × fraction
        num1, denom1 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        if self.difficulty == "current":
            multiplier = random.randint(1, 5)
            num2 = multiplier
            denom2 = 1
            operation_desc = f"{num1}/{denom1} × {multiplier}"
        else:
            num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)
            operation_desc = f"{num1}/{denom1} × {num2}/{denom2}"

        result_num = num1 * num2
        result_denom = denom1 * denom2
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, result_denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "×",
            "fraction1": {"numerator": num1, "denominator": denom1},
            "fraction2": {"numerator": num2, "denominator": denom2},
            "description": f"{operation_desc} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"כפול מונים: {num1} × {num2} = {result_num}",
                f"כפול מכנים: {denom1} × {denom2} = {result_denom}",
                f"אם צריך, צמצם: {result_num}/{result_denom} = {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="multiplication",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def _generate_division(self, variant_num: int) -> Exercise:
        """Generate division of fractions (advanced)"""
        num1, denom1 = self.randomize_fraction(self.numerator_range, self.denominator_range)
        num2, denom2 = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Division = multiply by reciprocal
        result_num = num1 * denom2
        result_denom = denom1 * num2
        result_num_simp, result_denom_simp = MathUtils.simplify_fraction(result_num, result_denom)

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "operation",
            "operation": "÷",
            "fraction1": {"numerator": num1, "denominator": denom1},
            "fraction2": {"numerator": num2, "denominator": denom2},
            "description": f"{num1}/{denom1} ÷ {num2}/{denom2} = ___"
        }

        answer = {
            "result": {"numerator": result_num_simp, "denominator": result_denom_simp},
            "steps": [
                f"חילוק = כפל בהופכי",
                f"{num1}/{denom1} ÷ {num2}/{denom2} = {num1}/{denom1} × {denom2}/{num2}",
                f"כפול: {num1 * denom2}/{denom1 * num2}",
                f"צמצם: {result_num_simp}/{result_denom_simp}"
            ]
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="division",
            topic="fraction_operations",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["add_subtract"],
            visual_required=False
        )

    def validate_exercise(self, exercise: Exercise) -> bool:
        """Validate exercise correctness"""
        try:
            result = exercise.answer.get("result")
            if result["denominator"] == 0:
                return False
            return True
        except Exception:
            return False
