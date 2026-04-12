"""
Visual Rendering Module

Generates SVG visualizations for fraction exercises:
- Grid representations
- Pie charts
- Number lines
"""

import math
from typing import Tuple, List, Optional


class SVGRenderer:
    """Generate SVG graphics for math exercises"""

    @staticmethod
    def generate_grid(
        rows: int,
        cols: int,
        shaded_cells: Optional[List[Tuple[int, int]]] = None,
        cell_size: int = 30
    ) -> str:
        """
        Generate SVG grid with optional shading.

        Args:
            rows: Number of rows
            cols: Number of columns
            shaded_cells: List of (row, col) tuples to shade
            cell_size: Size of each cell in pixels

        Returns:
            SVG string
        """
        width = cols * cell_size + 2
        height = rows * cell_size + 2

        svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Draw grid
        for row in range(rows):
            for col in range(cols):
                x = col * cell_size + 1
                y = row * cell_size + 1

                # Check if cell should be shaded
                is_shaded = shaded_cells and (row, col) in shaded_cells

                fill_color = "#3498db" if is_shaded else "#ffffff"
                svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                svg += f'fill="{fill_color}" stroke="#2c3e50" stroke-width="1"/>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def generate_pie_chart(
        total_sections: int,
        shaded_sections: int,
        radius: int = 50
    ) -> str:
        """
        Generate SVG pie chart.

        Args:
            total_sections: Total number of sections
            shaded_sections: Number of shaded sections
            radius: Radius of pie in pixels

        Returns:
            SVG string
        """
        center_x = radius + 10
        center_y = radius + 10
        svg_size = (radius + 10) * 2

        svg = f'<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg">\n'

        angle_per_section = 360 / total_sections
        current_angle = 0

        for i in range(total_sections):
            is_shaded = i < shaded_sections

            start_angle = current_angle
            end_angle = current_angle + angle_per_section

            # Convert to radians
            start_rad = math.radians(start_angle - 90)
            end_rad = math.radians(end_angle - 90)

            # Calculate points
            x1 = center_x + radius * math.cos(start_rad)
            y1 = center_y + radius * math.sin(start_rad)
            x2 = center_x + radius * math.cos(end_rad)
            y2 = center_y + radius * math.sin(end_rad)

            # Large arc flag
            large_arc = 1 if angle_per_section > 180 else 0

            fill_color = "#e74c3c" if is_shaded else "#ecf0f1"

            path = f"M {center_x} {center_y} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            svg += f'<path d="{path}" fill="{fill_color}" stroke="#2c3e50" stroke-width="1"/>\n'

            current_angle = end_angle

        svg += '</svg>'
        return svg

    @staticmethod
    def generate_number_line(
        min_val: float = 0,
        max_val: float = 1,
        marked_point: Optional[float] = None,
        width: int = 400,
        height: int = 50
    ) -> str:
        """
        Generate SVG number line.

        Args:
            min_val: Minimum value on line
            max_val: Maximum value on line
            marked_point: Point to mark with arrow
            width: Width in pixels
            height: Height in pixels

        Returns:
            SVG string
        """
        padding = 30
        line_y = height // 2
        line_start_x = padding
        line_end_x = width - padding

        svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Draw main line
        svg += f'<line x1="{line_start_x}" y1="{line_y}" x2="{line_end_x}" y2="{line_y}" '
        svg += 'stroke="#2c3e50" stroke-width="2"/>\n'

        # Draw tick marks and labels
        num_ticks = 11  # 0 to 1 with 0.1 increments
        for i in range(num_ticks):
            ratio = i / (num_ticks - 1)
            x = line_start_x + (line_end_x - line_start_x) * ratio
            val = min_val + (max_val - min_val) * ratio

            # Tick mark
            svg += f'<line x1="{x}" y1="{line_y - 5}" x2="{x}" y2="{line_y + 5}" '
            svg += 'stroke="#2c3e50" stroke-width="1"/>\n'

            # Label
            svg += f'<text x="{x}" y="{line_y + 20}" text-anchor="middle" '
            svg += f'font-family="Arial" font-size="10" fill="#2c3e50">{val:.1f}</text>\n'

        # Mark specific point if provided
        if marked_point is not None:
            ratio = (marked_point - min_val) / (max_val - min_val)
            x = line_start_x + (line_end_x - line_start_x) * ratio

            # Draw arrow pointing to point
            arrow_size = 10
            svg += f'<polygon points="{x},{line_y - 15} {x - arrow_size},{line_y - 25} '
            svg += f'{x + arrow_size},{line_y - 25}" fill="#e74c3c"/>\n'

        svg += '</svg>'
        return svg

    @staticmethod
    def generate_grid_fraction_visual(
        numerator: int,
        denominator: int,
        grid_type: str = "square"
    ) -> str:
        """
        Generate visual representation of a fraction using grid.

        Args:
            numerator: Fraction numerator
            denominator: Fraction denominator
            grid_type: "square" or "bar"

        Returns:
            SVG string
        """
        if grid_type == "square":
            # Create square grid
            grid_size = int(math.ceil(math.sqrt(denominator)))
            shaded = list(range(numerator))

            # Create list of (row, col) tuples for shaded cells
            shaded_cells = []
            for idx in shaded:
                row = idx // grid_size
                col = idx % grid_size
                if row < grid_size and col < grid_size:
                    shaded_cells.append((row, col))

            return SVGRenderer.generate_grid(
                rows=grid_size,
                cols=grid_size,
                shaded_cells=shaded_cells,
                cell_size=30
            )
        else:
            # Bar representation
            return SVGRenderer.generate_grid(
                rows=1,
                cols=denominator,
                shaded_cells=[(0, i) for i in range(numerator)],
                cell_size=30
            )


class VisualAssetGenerator:
    """Generate and manage visual assets for exercises"""

    @staticmethod
    def embed_visual_in_html(
        exercise_type: str,
        exercise_data: dict,
        inline: bool = True
    ) -> str:
        """
        Generate HTML with embedded SVG for exercise.

        Args:
            exercise_type: Type of exercise
            exercise_data: Exercise question/answer data
            inline: If True, embed SVG inline; else reference file

        Returns:
            HTML string with visual
        """
        html = '<div class="visual-content">'

        if exercise_type == "grid_shading":
            fraction = exercise_data.get("fraction", {})
            num = fraction.get("numerator", 1)
            denom = fraction.get("denominator", 2)
            svg = SVGRenderer.generate_grid_fraction_visual(num, denom, grid_type="square")
            html += svg

        elif exercise_type in ["pie_identify", "pie_color"]:
            fraction = exercise_data.get("fraction", {})
            num = fraction.get("numerator", 1)
            denom = fraction.get("denominator", 2)
            svg = SVGRenderer.generate_pie_chart(denom, num)
            html += svg

        elif exercise_type in ["number_line_place", "number_line_identify"]:
            marked = exercise_data.get("decimal_value")
            svg = SVGRenderer.generate_number_line(marked_point=marked)
            html += svg

        elif exercise_type == "comparison_different_denom":
            # Show both fractions visually
            f1 = exercise_data.get("fraction1", {})
            f2 = exercise_data.get("fraction2", {})

            html += "<div style='display: flex; gap: 20px; justify-content: center;'>"
            html += "<div>" + SVGRenderer.generate_grid_fraction_visual(
                f1.get("numerator", 1), f1.get("denominator", 2)
            ) + "</div>"
            html += "<div>" + SVGRenderer.generate_grid_fraction_visual(
                f2.get("numerator", 1), f2.get("denominator", 2)
            ) + "</div>"
            html += "</div>"

        html += '</div>'
        return html


if __name__ == "__main__":
    # Test visual generation
    print(SVGRenderer.generate_grid(2, 2, [(0, 0), (1, 1)]))
    print(SVGRenderer.generate_pie_chart(4, 2))
    print(SVGRenderer.generate_number_line(marked_point=0.75))
