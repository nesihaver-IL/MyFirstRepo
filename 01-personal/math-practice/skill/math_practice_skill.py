"""
Math Practice Skill - Main Entry Point

Orchestrates exercise generation for 5th grade Hebrew mathematics.
Coordinates all topic generators and output formatting.
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Import all generators
from .generators.base_generator import ExerciseSet
from .generators.fraction_comparison import FractionComparisonGenerator
from .generators.fraction_operations import FractionOperationsGenerator
from .generators.mixed_numbers import MixedNumbersGenerator
from .generators.visual_fractions import VisualFractionsGenerator
from .generators.decimal_fractions import DecimalFractionsGenerator
from .visual_renderer import VisualAssetGenerator


class MathPracticeSkill:
    """
    Main skill interface for 5th grade math practice generation.

    Generates 10-15 pages of randomized exercises at current and advanced levels.
    """

    def __init__(
        self,
        project_root: str = "/home/nhaver/MyFirstRepo/01-personal/math-practice",
        seed: Optional[int] = None
    ):
        """
        Initialize the skill.

        Args:
            project_root: Path to math-practice project directory
            seed: Random seed for reproducibility
        """
        self.project_root = Path(project_root)
        self.skill_dir = self.project_root / "skill"
        self.curriculum_dir = self.project_root / "curriculum"
        self.output_dir = self.project_root / "output"
        self.seed = seed

        if seed is not None:
            random.seed(seed)

        # Load curriculum
        self.grade5_curriculum = self._load_curriculum("grade5_curriculum.json")
        self.grade6_curriculum = self._load_curriculum("grade6_curriculum.json")

    def _load_curriculum(self, filename: str) -> Dict[str, Any]:
        """Load curriculum JSON file"""
        curriculum_path = self.curriculum_dir / filename
        try:
            with open(curriculum_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Could not find {filename}")
            return {}

    def generate_practice_set(
        self,
        num_pages: int = 12,
        difficulty_mix: Tuple[float, float] = (0.7, 0.3),
        topics: Optional[List[str]] = None,
        exercises_per_page: int = 5
    ) -> List[ExerciseSet]:
        """
        Generate complete practice set.

        Args:
            num_pages: Number of pages to generate (10-15)
            difficulty_mix: (current_ratio, advanced_ratio), e.g., (0.7, 0.3)
            topics: Specific topics to include. If None, use all.
            exercises_per_page: Exercises per page (default 5)

        Returns:
            List of ExerciseSet objects, one per page
        """
        if num_pages < 10 or num_pages > 15:
            raise ValueError("num_pages must be between 10 and 15")

        # Initialize generators for all topics
        generators = self._create_generators()

        # If topics not specified, use all
        if topics is None:
            topics = list(generators.keys())

        # Generate exercises for all topics
        all_exercises = self._generate_all_exercises(
            generators, topics, difficulty_mix, exercises_per_page * num_pages
        )

        # Organize into pages
        pages = self._organize_into_pages(
            all_exercises, num_pages, exercises_per_page
        )

        return pages

    def _create_generators(self) -> Dict[str, List[Any]]:
        """Create all topic generators"""
        return {
            "fraction_comparison": [
                FractionComparisonGenerator(difficulty="current", seed=self.seed),
                FractionComparisonGenerator(difficulty="advanced", seed=self.seed)
            ],
            "fraction_operations": [
                FractionOperationsGenerator(difficulty="current", seed=self.seed),
                FractionOperationsGenerator(difficulty="advanced", seed=self.seed)
            ],
            "mixed_numbers": [
                MixedNumbersGenerator(difficulty="current", seed=self.seed),
                MixedNumbersGenerator(difficulty="advanced", seed=self.seed)
            ],
            "visual_fractions": [
                VisualFractionsGenerator(difficulty="current", seed=self.seed),
                VisualFractionsGenerator(difficulty="advanced", seed=self.seed)
            ],
            "decimal_fractions": [
                DecimalFractionsGenerator(difficulty="current", seed=self.seed),
                DecimalFractionsGenerator(difficulty="advanced", seed=self.seed)
            ]
        }

    def _generate_all_exercises(
        self,
        generators: Dict[str, List[Any]],
        topics: List[str],
        difficulty_mix: Tuple[float, float],
        total_count: int
    ) -> List[Any]:
        """Generate all exercises for all topics"""
        exercises = []

        # Calculate exercises per topic
        exercises_per_topic = total_count // len(topics)
        current_count = int(exercises_per_topic * difficulty_mix[0])
        advanced_count = exercises_per_topic - current_count

        for topic in topics:
            if topic not in generators:
                continue

            gen_current = generators[topic][0]
            gen_advanced = generators[topic][1]

            # Generate current level exercises
            current_exercises = gen_current.generate_exercises(current_count)
            exercises.extend(current_exercises)

            # Generate advanced level exercises
            advanced_exercises = gen_advanced.generate_exercises(advanced_count)
            exercises.extend(advanced_exercises)

        # Shuffle for variety
        random.shuffle(exercises)

        return exercises

    def _organize_into_pages(
        self,
        exercises: List[Any],
        num_pages: int,
        exercises_per_page: int
    ) -> List[ExerciseSet]:
        """Organize exercises into pages"""
        pages = []

        for page_num in range(num_pages):
            start_idx = page_num * exercises_per_page
            end_idx = start_idx + exercises_per_page

            page_exercises = exercises[start_idx:end_idx]

            # Create ExerciseSet for this page
            page_title = f"עמוד {page_num + 1}: תרגול שברים"
            page = ExerciseSet(
                title=page_title,
                exercises=page_exercises,
                metadata={
                    "page_number": page_num + 1,
                    "total_exercises": len(page_exercises),
                    "topics": list(set([e.topic for e in page_exercises])),
                    "difficulties": list(set([e.difficulty for e in page_exercises])),
                    "generated_at": datetime.now().isoformat()
                }
            )

            pages.append(page)

        return pages

    def export_to_json(
        self,
        pages: List[ExerciseSet],
        output_file: Optional[str] = None
    ) -> str:
        """Export exercises to JSON"""
        if output_file is None:
            output_file = str(self.output_dir / "exercises.json")

        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_pages": len(pages),
                "language": "Hebrew",
                "curriculum": "Israeli Grade 5 Mathematics"
            },
            "pages": [page.to_dict() for page in pages]
        }

        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Exported to {output_file}")
        return output_file

    def export_to_html(
        self,
        pages: List[ExerciseSet],
        output_dir: Optional[str] = None
    ) -> List[str]:
        """Export exercises to HTML pages"""
        if output_dir is None:
            output_dir = str(self.output_dir / "pages_html")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        output_files = []

        for page in pages:
            html_content = self._generate_html_page(page)
            filename = f"page_{page.metadata['page_number']:02d}.html"
            filepath = Path(output_dir) / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            output_files.append(str(filepath))
            print(f"✓ Generated {filename}")

        return output_files

    def export_to_single_html(
        self,
        pages: List[ExerciseSet],
        output_file: Optional[str] = None
    ) -> str:
        """Export all exercises to a single HTML file for printing"""
        if output_file is None:
            output_file = str(self.output_dir / "complete_practice_book.html")

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        html = self._generate_combined_html(pages)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✓ Generated combined HTML: {Path(output_file).name}")
        return output_file

    def _generate_combined_html(self, pages: List[ExerciseSet]) -> str:
        """Generate a single HTML file combining all pages for printing"""
        html = """<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hebrew 5th Grade Math Practice - Complete Book</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', 'Tahoma', sans-serif;
            padding: 0;
            background: #f5f5f5;
            line-height: 1.6;
        }

        /* Cover Page */
        .cover-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            page-break-after: always;
            padding: 40px;
        }

        .cover-title {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 20px;
            direction: rtl;
        }

        .cover-subtitle {
            font-size: 24px;
            margin-bottom: 40px;
            direction: rtl;
        }

        .cover-content {
            font-size: 16px;
            line-height: 2;
            direction: rtl;
            max-width: 600px;
        }

        .cover-meta {
            margin-top: 50px;
            font-size: 14px;
            opacity: 0.9;
        }

        /* Table of Contents */
        .toc-page {
            page-break-after: always;
            padding: 40px 60px;
            background: white;
        }

        .toc-title {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 40px;
            color: #333;
            direction: rtl;
        }

        .toc-list {
            direction: rtl;
            text-align: right;
        }

        .toc-item {
            padding: 8px 0;
            border-bottom: 1px dotted #ccc;
            font-size: 14px;
        }

        /* Main Content Pages */
        .print-page {
            background: white;
            padding: 40px 30px;
            page-break-after: always;
            min-height: 100vh;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }

        .page-number-right {
            font-size: 12px;
            color: #999;
            direction: rtl;
        }

        .page-number-left {
            font-size: 12px;
            color: #999;
            direction: ltr;
        }

        .page-title {
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            direction: rtl;
            text-align: center;
            flex: 1;
        }

        .exercises-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .exercise-container {
            display: flex;
            min-height: 100px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            page-break-inside: avoid;
        }

        .exercise-left {
            flex: 1;
            padding: 15px;
            background: #f9f9f9;
            direction: ltr;
            text-align: left;
            border-right: 2px solid #667eea;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }

        .exercise-right {
            flex: 1;
            padding: 15px;
            background: #ffffff;
            direction: rtl;
            text-align: right;
        }

        .exercise-number {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 13px;
        }

        .exercise-question {
            font-size: 16px;
            color: #2c3e50;
            font-family: 'Courier New', monospace;
            margin-bottom: 12px;
            padding: 8px;
            background: #f0f8ff;
            border-radius: 3px;
            line-height: 1.6;
        }

        .answer-space {
            border-bottom: 2px solid #2c3e50;
            height: 30px;
            margin-top: 8px;
            width: 75%;
        }

        .visual-area {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 8px;
            min-height: 50px;
        }

        .visual-area svg {
            max-width: 95%;
            height: auto;
        }

        .exercise-instruction {
            color: #555555;
            font-size: 12px;
            line-height: 1.5;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 3px;
        }

        .instruction-label {
            font-weight: bold;
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }

        /* Footer */
        .page-footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            font-size: 11px;
            color: #999;
            direction: rtl;
        }

        /* Print Styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .print-page {
                box-shadow: none;
                page-break-after: always;
                padding: 30px 25px;
            }

            .cover-page {
                height: auto;
                min-height: 100vh;
            }

            .exercise-container {
                page-break-inside: avoid;
            }

            a {
                text-decoration: none;
            }
        }

        @page {
            size: A4;
            margin: 20mm;
        }
    </style>
</head>
<body>
"""

        # Cover Page
        html += """
    <!-- COVER PAGE -->
    <div class="cover-page">
        <div class="cover-title">תרגול מתמטיקה</div>
        <div class="cover-subtitle">כיתה ה׳ - שברים ופעולות</div>
        <div class="cover-content">
            <div>ספר תרגילים מקומפל</div>
            <div>עם תרגילים ברמת התחילה וברמה מתקדמת</div>
            <div style="margin-top: 20px;">📚 12 עמודים | 60 תרגילים</div>
        </div>
        <div class="cover-meta">
            <div>נוצר על ידי Math Practice Skill</div>
            <div style="margin-top: 10px;">2026</div>
        </div>
    </div>
"""

        # Table of Contents
        html += """
    <!-- TABLE OF CONTENTS -->
    <div class="toc-page">
        <div class="toc-title">תוכן עניינים</div>
        <div class="toc-list">
"""

        for page_num in range(1, len(pages) + 1):
            html += f"""            <div class="toc-item">עמוד {page_num}: תרגול שברים</div>
"""

        html += """        </div>
    </div>
"""

        # Content Pages
        for page in pages:
            html += self._generate_combined_page_content(page)

        # Back Cover
        html += """
    <!-- BACK COVER -->
    <div class="cover-page" style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);">
        <div style="font-size: 28px; font-weight: bold; direction: rtl; color: white; margin-bottom: 30px;">
            סיום הספר
        </div>
        <div style="font-size: 16px; direction: rtl; color: white; line-height: 2;">
            <div>כל הכבוד על השלמת התרגילים!</div>
            <div style="margin-top: 20px; font-size: 14px; opacity: 0.9;">
                המשך לתרגל ולשלוט בשברים
            </div>
        </div>
    </div>

</body>
</html>
"""
        return html

    def _generate_combined_page_content(self, page: ExerciseSet) -> str:
        """Generate content for a single page in combined HTML"""
        page_num = page.metadata['page_number']
        html = f"""
    <!-- PAGE {page_num} -->
    <div class="print-page">
        <div class="page-header">
            <div class="page-number-left">עמוד {page_num}</div>
            <div class="page-title">{page.title}</div>
            <div class="page-number-right">עמוד {page_num}</div>
        </div>

        <div class="exercises-container">
"""

        for idx, exercise in enumerate(page.exercises, 1):
            html += """            <div class="exercise-container">
                <!-- LEFT SIDE: NUMERIC EXERCISE (LTR) -->
                <div class="exercise-left">
"""
            html += f"""                    <div class="exercise-question">{exercise.question.get('description', 'תרגיל')}</div>
"""

            if exercise.visual_required:
                try:
                    visual_html = VisualAssetGenerator.embed_visual_in_html(
                        exercise.exercise_type,
                        exercise.question,
                        inline=True
                    )
                    html += f"""                    <div class="visual-area">
                        {visual_html}
                    </div>
"""
                except Exception:
                    pass

            html += """                    <div class="answer-space"></div>
                </div>

                <!-- RIGHT SIDE: HEBREW INSTRUCTIONS (RTL) -->
                <div class="exercise-right">
"""
            # Find exercise number in page
            exercise_num = idx
            html += f"""                    <span class="exercise-number">תרגיל {exercise_num}</span>
                    <div class="exercise-instruction">
                        <span class="instruction-label">הוראות:</span>
                        {exercise.instructions}
                    </div>
                </div>
            </div>
"""

        html += """        </div>

        <div class="page-footer">
            ספר תרגול מתמטיקה | כיתה ה׳ | עמוד """ + str(page_num) + """
        </div>
    </div>
"""

        return html

    def _generate_html_page(self, page: ExerciseSet) -> str:
        """Generate HTML for a single page with split RTL/LTR layout"""
        html = f"""<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Arial', 'Tahoma', sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }}

        .page-container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .page-title {{
            text-align: center;
            margin-bottom: 40px;
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            direction: rtl;
        }}

        .exercise-container {{
            display: flex;
            margin-bottom: 30px;
            min-height: 120px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }}

        .exercise-left {{
            flex: 1;
            padding: 20px;
            background: #f9f9f9;
            direction: ltr;
            text-align: left;
            border-right: 2px solid #3498db;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}

        .exercise-right {{
            flex: 1;
            padding: 20px;
            background: #ffffff;
            direction: rtl;
            text-align: right;
        }}

        .exercise-number {{
            font-weight: bold;
            color: #3498db;
            margin-bottom: 15px;
            font-size: 14px;
        }}

        .exercise-question {{
            font-size: 18px;
            color: #2c3e50;
            font-family: 'Courier New', monospace;
            margin-bottom: 15px;
            padding: 10px;
            background: #f0f8ff;
            border-radius: 4px;
            line-height: 1.8;
        }}

        .answer-space {{
            border-bottom: 2px solid #2c3e50;
            height: 35px;
            margin-top: 10px;
            width: 80%;
        }}

        .visual-area {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
            min-height: 60px;
        }}

        .visual-area svg {{
            max-width: 95%;
            height: auto;
        }}

        .exercise-instruction {{
            color: #555555;
            font-size: 13px;
            margin-bottom: 12px;
            line-height: 1.6;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 3px;
        }}

        .instruction-label {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }}

        @media print {{
            body {{ background: white; }}
            .page-container {{ box-shadow: none; border: none; }}
            .exercise-container {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <div class="page-title" dir="rtl">{page.title}</div>
"""

        for idx, exercise in enumerate(page.exercises, 1):
            html += """
        <div class="exercise-container">
            <!-- LEFT SIDE: NUMERIC EXERCISE (LTR) -->
            <div class="exercise-left">
"""
            html += f"""                <div class="exercise-question">{exercise.question.get('description', 'תרגיל')}</div>
"""

            if exercise.visual_required:
                try:
                    visual_html = VisualAssetGenerator.embed_visual_in_html(
                        exercise.exercise_type,
                        exercise.question,
                        inline=True
                    )
                    html += f"""                <div class="visual-area">
                    {visual_html}
                </div>
"""
                except Exception:
                    pass

            html += """                <div class="answer-space"></div>
            </div>

            <!-- RIGHT SIDE: HEBREW INSTRUCTIONS (RTL) -->
            <div class="exercise-right">
"""
            html += f"""                <span class="exercise-number">תרגיל {idx}</span>
                <div class="exercise-instruction">
                    <span class="instruction-label">הוראות:</span>
                    {exercise.instructions}
                </div>
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""
        return html

    def export_to_docx(
        self,
        pages: List[ExerciseSet],
        output_dir: Optional[str] = None
    ) -> List[str]:
        """Export exercises to DOCX files"""
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            print("Warning: python-docx not installed. Skipping DOCX export.")
            return []

        if output_dir is None:
            output_dir = str(self.output_dir / "pages_docx")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        output_files = []

        for page in pages:
            doc = Document()

            # Set RTL for Hebrew
            section = doc.sections[0]
            section.right_margin = Inches(1)
            section.left_margin = Inches(1)

            # Title
            title = doc.add_paragraph()
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title.add_run(page.title)
            title_run.font.size = Pt(18)
            title_run.font.bold = True

            # Exercises
            for idx, exercise in enumerate(page.exercises, 1):
                p = doc.add_paragraph()
                p_run = p.add_run(f"תרגיל {idx}: ")
                p_run.font.bold = True
                p.add_run(exercise.question.get("description", "תרגיל"))

                p_instruction = doc.add_paragraph(exercise.instructions)
                p_instruction.paragraph_format.left_indent = Inches(0.25)

                # Add space for answer
                doc.add_paragraph("_" * 40)

                if exercise.visual_required:
                    doc.add_paragraph("[תמונה יוספת כאן]")

                doc.add_paragraph()  # Space between exercises

            filename = f"page_{page.metadata['page_number']:02d}.docx"
            filepath = Path(output_dir) / filename
            doc.save(str(filepath))

            output_files.append(str(filepath))
            print(f"✓ Generated {filename}")

        return output_files

    def generate_complete_package(
        self,
        num_pages: int = 12,
        difficulty_mix: Tuple[float, float] = (0.7, 0.3)
    ) -> Dict[str, List[str]]:
        """
        Generate complete package: JSON + HTML + DOCX

        Returns:
            Dictionary with keys 'json', 'html', 'docx' and file paths
        """
        print(f"\n📚 Generating {num_pages} pages of practice exercises...\n")

        # Generate exercises
        pages = self.generate_practice_set(
            num_pages=num_pages,
            difficulty_mix=difficulty_mix
        )

        print(f"✓ Generated {len(pages)} pages with {sum(len(p.exercises) for p in pages)} exercises\n")

        # Export to all formats
        print("💾 Exporting to formats...\n")

        result = {
            "json": [self.export_to_json(pages)],
            "html": self.export_to_html(pages),
            "docx": self.export_to_docx(pages)
        }

        print(f"\n✅ Complete package generated!")
        print(f"📁 Output directory: {self.output_dir}")

        return result


# CLI Usage
if __name__ == "__main__":
    skill = MathPracticeSkill()

    # Generate practice set
    result = skill.generate_complete_package(
        num_pages=12,
        difficulty_mix=(0.7, 0.3)  # 70% current, 30% advanced
    )

    print(f"\n📊 Generation Summary:")
    print(f"   JSON files: {len(result['json'])}")
    print(f"   HTML pages: {len(result['html'])}")
    print(f"   DOCX files: {len(result['docx'])}")
