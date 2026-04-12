"""
Base Generator Class for Math Exercises

Provides common functionality for all exercise generators:
- Fraction validation and simplification
- Randomization with seeding
- Hebrew text generation
- Exercise structure
"""

import random
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Any
from math import gcd
from functools import reduce


class MathUtils:
    """Utility functions for fraction mathematics"""

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor"""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate least common multiple"""
        return abs(a * b) // MathUtils.gcd(a, b)

    @staticmethod
    def lcm_multiple(numbers: List[int]) -> int:
        """Calculate LCM of multiple numbers"""
        return reduce(MathUtils.lcm, numbers)

    @staticmethod
    def simplify_fraction(numerator: int, denominator: int) -> Tuple[int, int]:
        """Reduce fraction to lowest terms"""
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
        if numerator == 0:
            return (0, 1)

        g = MathUtils.gcd(abs(numerator), abs(denominator))
        simplified_num = numerator // g
        simplified_denom = denominator // g

        # Ensure denominator is positive
        if simplified_denom < 0:
            simplified_num = -simplified_num
            simplified_denom = -simplified_denom

        return (simplified_num, simplified_denom)

    @staticmethod
    def is_equivalent(num1: int, denom1: int, num2: int, denom2: int) -> bool:
        """Check if two fractions are equivalent"""
        simp1 = MathUtils.simplify_fraction(num1, denom1)
        simp2 = MathUtils.simplify_fraction(num2, denom2)
        return simp1 == simp2

    @staticmethod
    def compare_fractions(num1: int, denom1: int, num2: int, denom2: int) -> int:
        """
        Compare two fractions.
        Returns: -1 if f1 < f2, 0 if f1 == f2, 1 if f1 > f2
        """
        # Cross multiply to compare without floating point
        cross1 = num1 * denom2
        cross2 = num2 * denom1

        if cross1 < cross2:
            return -1
        elif cross1 > cross2:
            return 1
        else:
            return 0

    @staticmethod
    def improper_to_mixed(numerator: int, denominator: int) -> Tuple[int, int, int]:
        """
        Convert improper fraction to mixed number.
        Returns: (whole, numerator, denominator)
        """
        whole = numerator // denominator
        remaining_num = numerator % denominator
        return (whole, remaining_num, denominator)

    @staticmethod
    def mixed_to_improper(whole: int, numerator: int, denominator: int) -> Tuple[int, int]:
        """
        Convert mixed number to improper fraction.
        Returns: (numerator, denominator)
        """
        improper_num = whole * denominator + numerator
        return (improper_num, denominator)

    @staticmethod
    def format_fraction_string(numerator: int, denominator: int) -> str:
        """Format fraction as string"""
        return f"{numerator}/{denominator}"

    @staticmethod
    def format_mixed_string(whole: int, numerator: int, denominator: int) -> str:
        """Format mixed number as string"""
        if whole == 0:
            return f"{numerator}/{denominator}"
        return f"{whole} {numerator}/{denominator}"


class HebrewText:
    """Hebrew text generation for exercises"""

    # Hebrew number words
    HEBREW_NUMBERS = {
        0: "אפס", 1: "אחד", 2: "שניים", 3: "שלוש", 4: "ארבע",
        5: "חמש", 6: "שש", 7: "שבע", 8: "שמונה", 9: "תשע",
        10: "עשר"
    }

    # Hebrew mathematical operators
    OPERATORS = {
        ">": "גדול מ",
        "<": "קטן מ",
        "=": "שווה ל",
        "+": "חיבור",
        "-": "חיסור",
        "×": "כפל",
        "÷": "חילוק"
    }

    # Hebrew instructions for different exercise types
    INSTRUCTIONS = {
        "compare": "בחר את הסימן הנכון: > , < , =",
        "simplify": "צמצם את השבר לצורה מצומצמת",
        "convert_mixed": "המר בין מספר מעורב לשבר גדול מ-1",
        "add_subtract": "חשב את הפעולה ובטא את התשובה כשבר מצומצם",
        "visual": "זהה או צייר את השבר על פי התמונה",
        "decimal": "המר בין עשרוני לשבר"
    }

    @staticmethod
    def hebrew_fraction(numerator: int, denominator: int) -> str:
        """Format fraction in Hebrew"""
        return f"{numerator}/{denominator}"

    @staticmethod
    def get_instruction(exercise_type: str) -> str:
        """Get Hebrew instruction for exercise type"""
        return HebrewText.INSTRUCTIONS.get(exercise_type, "פתור את התרגיל")


class Exercise:
    """Structure for a single exercise"""

    def __init__(
        self,
        exercise_id: str,
        exercise_type: str,
        topic: str,
        difficulty: str,
        question: Dict[str, Any],
        answer: Dict[str, Any],
        instructions: str,
        visual_required: bool = False
    ):
        self.exercise_id = exercise_id
        self.exercise_type = exercise_type
        self.topic = topic
        self.difficulty = difficulty
        self.question = question
        self.answer = answer
        self.instructions = instructions
        self.visual_required = visual_required

    def to_dict(self) -> Dict[str, Any]:
        """Convert exercise to dictionary"""
        return {
            "id": self.exercise_id,
            "type": self.exercise_type,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "question": self.question,
            "answer": self.answer,
            "instructions": self.instructions,
            "visual_required": self.visual_required
        }


class BaseGenerator(ABC):
    """
    Abstract base class for all exercise generators.

    Subclasses should implement:
    - generate_exercise(): Create a single exercise
    - validate_exercise(): Verify exercise correctness
    """

    def __init__(
        self,
        topic_id: str,
        difficulty: str = "current",
        seed: Optional[int] = None
    ):
        """
        Initialize generator.

        Args:
            topic_id: Unique identifier for topic
            difficulty: "current" (5th grade) or "advanced" (6th grade)
            seed: Random seed for reproducibility
        """
        self.topic_id = topic_id
        self.difficulty = difficulty
        self.seed = seed

        if seed is not None:
            random.seed(seed)

    @abstractmethod
    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """
        Generate a single exercise variant.

        Args:
            variant_num: Exercise variant number (for tracking)

        Returns:
            Exercise object
        """
        pass

    @abstractmethod
    def validate_exercise(self, exercise: Exercise) -> bool:
        """
        Validate that exercise is correctly formed.

        Args:
            exercise: Exercise to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def generate_exercises(self, count: int) -> List[Exercise]:
        """
        Generate multiple exercise variants.

        Args:
            count: Number of exercises to generate

        Returns:
            List of Exercise objects
        """
        exercises = []
        for i in range(count):
            try:
                exercise = self.generate_exercise(variant_num=i)
                if self.validate_exercise(exercise):
                    exercises.append(exercise)
            except Exception as e:
                print(f"Error generating exercise {i}: {e}")
                continue

        return exercises

    def randomize_fraction(
        self,
        numerator_range: Tuple[int, int],
        denominator_range: Tuple[int, int],
        exclude_whole: bool = True
    ) -> Tuple[int, int]:
        """
        Generate random fraction within ranges.

        Args:
            numerator_range: (min, max) for numerator
            denominator_range: (min, max) for denominator
            exclude_whole: If True, exclude fractions where num >= denom

        Returns:
            (numerator, denominator) tuple
        """
        while True:
            num = random.randint(*numerator_range)
            denom = random.randint(*denominator_range)

            # Avoid denominator of 1
            if denom == 1:
                denom = random.randint(2, denominator_range[1])

            # Skip if whole number and exclude_whole=True
            if exclude_whole and num >= denom:
                continue

            return (num, denom)

    def randomize_whole_and_fraction(
        self,
        whole_range: Tuple[int, int],
        numerator_range: Tuple[int, int],
        denominator_range: Tuple[int, int]
    ) -> Tuple[int, int, int]:
        """
        Generate random mixed number.

        Returns:
            (whole, numerator, denominator) tuple
        """
        whole = random.randint(*whole_range)
        num = random.randint(*numerator_range)
        denom = random.randint(*denominator_range)

        # Ensure denominator > numerator
        while num >= denom:
            num = random.randint(*numerator_range)
            denom = random.randint(*denominator_range)

        return (whole, num, denom)

    def get_exercise_id(self, variant_num: int) -> str:
        """Generate unique exercise ID"""
        return f"{self.topic_id}_{self.difficulty}_v{variant_num}"


class ExerciseSet:
    """Container for a set of exercises with metadata"""

    def __init__(
        self,
        title: str,
        exercises: List[Exercise],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.exercises = exercises
        self.metadata = metadata or {}
        self.created_timestamp = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert exercise set to dictionary"""
        return {
            "title": self.title,
            "count": len(self.exercises),
            "metadata": self.metadata,
            "exercises": [e.to_dict() for e in self.exercises]
        }


# Test helper functions
def test_math_utils():
    """Quick validation of MathUtils"""
    assert MathUtils.gcd(12, 8) == 4
    assert MathUtils.simplify_fraction(4, 8) == (1, 2)
    assert MathUtils.is_equivalent(1, 2, 2, 4) == True
    assert MathUtils.compare_fractions(1, 2, 2, 3) == -1
    assert MathUtils.improper_to_mixed(7, 4) == (1, 3, 4)
    assert MathUtils.mixed_to_improper(1, 3, 4) == (7, 4)
    print("✓ MathUtils tests passed")


if __name__ == "__main__":
    test_math_utils()
