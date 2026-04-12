"""
Visual Fractions Exercise Generator

Generates exercises using visual representations: grids, pie charts, and number lines.
"""

import random
from typing import Tuple, Dict, Any, Optional, List
from .base_generator import BaseGenerator, Exercise, MathUtils, HebrewText


class VisualFractionsGenerator(BaseGenerator):
    """Generate visual fraction exercises"""

    def __init__(
        self,
        difficulty: str = "current",
        seed: Optional[int] = None,
        numerator_range: Tuple[int, int] = (1, 8),
        denominator_range: Tuple[int, int] = (2, 12)
    ):
        super().__init__("visual_fractions", difficulty, seed)
        self.numerator_range = numerator_range
        self.denominator_range = denominator_range

    def generate_exercise(self, variant_num: int = 0) -> Exercise:
        """Generate a visual fraction exercise"""

        visual_type = random.choice(["grid_shading", "grid_identify", "pie_chart", "number_line"])

        if visual_type == "grid_shading":
            return self._generate_grid_shading(variant_num)
        elif visual_type == "grid_identify":
            return self._generate_grid_identify(variant_num)
        elif visual_type == "pie_chart":
            return self._generate_pie_chart(variant_num)
        else:
            return self._generate_number_line(variant_num)

    def _generate_grid_shading(self, variant_num: int) -> Exercise:
        """Generate exercise: shade the given fraction in a grid"""
        num, denom = self.randomize_fraction(self.numerator_range, self.denominator_range)

        # Choose grid size (square for simplicity)
        grid_size = denom
        if grid_size > 12:
            grid_size = 12
        if grid_size < 2:
            grid_size = 2

        # Calculate how many cells to shade
        cells_to_shade = num if num < grid_size else grid_size - 1

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "visual",
            "visual_type": "grid_shading",
            "fraction": {"numerator": num, "denominator": denom},
            "grid_size": grid_size,
            "description": f"הצל {num}/{denom} של הרשת"
        }

        answer = {
            "fraction": {"numerator": num, "denominator": denom},
            "cells_to_shade": cells_to_shade,
            "total_cells": grid_size,
            "explanation": f"הצל {cells_to_shade} ריבועים מתוך {grid_size}"
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="grid_shading",
            topic="visual_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["visual"],
            visual_required=True
        )

    def _generate_grid_identify(self, variant_num: int) -> Exercise:
        """Generate exercise: identify the fraction from a shaded grid"""
        num, denom = self.randomize_fraction(self.numerator_range, self.denominator_range)

        grid_size = denom
        if grid_size > 12:
            grid_size = 12

        shaded_cells = num

        exercise_id = self.get_exercise_id(variant_num)

        question = {
            "type": "visual",
            "visual_type": "grid_identify",
            "grid_size": grid_size,
            "shaded_cells": shaded_cells,
            "description": f"איזה שבר מייצג ההצללה?"
        }

        # Simplify fraction for answer
        num_simp, denom_simp = MathUtils.simplify_fraction(shaded_cells, grid_size)

        answer = {
            "fraction": {"numerator": num_simp, "denominator": denom_simp},
            "unsimplified": {"numerator": shaded_cells, "denominator": grid_size},
            "explanation": f"{shaded_cells} ריבועים מ-{grid_size} = {num_simp}/{denom_simp}"
        }

        return Exercise(
            exercise_id=exercise_id,
            exercise_type="grid_identify",
            topic="visual_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["visual"],
            visual_required=True
        )

    def _generate_pie_chart(self, variant_num: int) -> Exercise:
        """Generate exercise with pie chart"""
        # Use simple denominators for pie charts: 2, 4, 8, etc.
        denom = random.choice([2, 3, 4, 6, 8, 12])
        num = random.randint(1, denom - 1)

        # Simplify for display
        num_simp, denom_simp = MathUtils.simplify_fraction(num, denom)

        exercise_type = random.choice(["identify_pie", "color_pie"])
        exercise_id = self.get_exercise_id(variant_num)

        if exercise_type == "identify_pie":
            question = {
                "type": "visual",
                "visual_type": "pie_identify",
                "colored_sections": num,
                "total_sections": denom,
                "description": f"איזה חלק של העוגה צבוע?"
            }

            answer = {
                "fraction": {"numerator": num_simp, "denominator": denom_simp},
                "explanation": f"{num} קטעים צבועים מ-{denom} קטעים כולל = {num_simp}/{denom_simp}"
            }

            ex_type = "pie_identify"

        else:  # color_pie
            question = {
                "type": "visual",
                "visual_type": "pie_color",
                "total_sections": denom,
                "fraction": {"numerator": num_simp, "denominator": denom_simp},
                "description": f"צבע {num_simp}/{denom_simp} של העוגה"
            }

            answer = {
                "fraction": {"numerator": num_simp, "denominator": denom_simp},
                "sections_to_color": num,
                "total_sections": denom,
                "explanation": f"צבע {num} קטעים מ-{denom}"
            }

            ex_type = "pie_color"

        return Exercise(
            exercise_id=exercise_id,
            exercise_type=ex_type,
            topic="visual_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["visual"],
            visual_required=True
        )

    def _generate_number_line(self, variant_num: int) -> Exercise:
        """Generate exercise with number line"""
        num, denom = self.randomize_fraction(self.numerator_range, (2, 8))

        # Create a number line with 0 and 1
        exercise_type = random.choice(["place_on_line", "identify_point"])
        exercise_id = self.get_exercise_id(variant_num)

        if exercise_type == "place_on_line":
            question = {
                "type": "visual",
                "visual_type": "number_line_place",
                "fraction": {"numerator": num, "denominator": denom},
                "description": f"סמן את {num}/{denom} על ציר המספרים"
            }

            answer = {
                "fraction": {"numerator": num, "denominator": denom},
                "decimal_value": num / denom,
                "explanation": f"{num}/{denom} = {num/denom:.2f}"
            }

            ex_type = "number_line_place"

        else:  # identify_point
            position = num / denom
            question = {
                "type": "visual",
                "visual_type": "number_line_identify",
                "marked_position": position,
                "description": f"איזה שבר מסומן בחץ?"
            }

            answer = {
                "fraction": {"numerator": num, "denominator": denom},
                "decimal_value": position,
                "explanation": f"הנקודה היא ב-{position:.2f} = {num}/{denom}"
            }

            ex_type = "number_line_identify"

        return Exercise(
            exercise_id=exercise_id,
            exercise_type=ex_type,
            topic="visual_fractions",
            difficulty=self.difficulty,
            question=question,
            answer=answer,
            instructions=HebrewText.INSTRUCTIONS["visual"],
            visual_required=True
        )

    def validate_exercise(self, exercise: Exercise) -> bool:
        """Validate exercise correctness"""
        try:
            if "fraction" in exercise.answer:
                frac = exercise.answer["fraction"]
                if frac["denominator"] == 0:
                    return False

            if "grid_size" in exercise.question:
                if exercise.question["grid_size"] <= 0:
                    return False

            return True
        except Exception:
            return False
