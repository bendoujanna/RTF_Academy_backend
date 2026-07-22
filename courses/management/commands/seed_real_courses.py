# courses/management/commands/seed_real_courses.py
#
# Seeds the database with real RTF Academy course content.
# Place this file at:
#   courses/management/commands/seed_real_courses.py
#
# Also place rtf_academy_courses_refined.json in the project root (same folder as manage.py).
#
# Run with:
#   python manage.py seed_real_courses
#
# The command is fully IDEMPOTENT — safe to run multiple times.
# Existing courses (matched by title) are skipped, not duplicated.

import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from courses.models import Course, Module, Lesson
from quizzes.models import AnswerChoice, Question, Quiz


class Command(BaseCommand):
    help = "Seeds real RTF Academy course content from rtf_academy_courses_refined.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            type=str,
            default=None,
            help="Path to the refined JSON file. Defaults to rtf_academy_courses_refined.json in BASE_DIR.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Delete and recreate courses that already exist instead of skipping them.",
        )

    def handle(self, *args, **options):
        # ── Locate JSON file ──────────────────────────────────────────────────
        json_path = options["json"] or os.path.join(
            settings.BASE_DIR, "rtf_academy_courses_refined.json"
        )

        if not os.path.exists(json_path):
            self.stderr.write(
                self.style.ERROR(
                    f"JSON file not found: {json_path}\n"
                    "Place rtf_academy_courses_refined.json in the project root "
                    "or pass --json <path>."
                )
            )
            return

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        courses_data = data.get("courses", [])
        self.stdout.write(f"Found {len(courses_data)} course(s) to import.\n")

        created_courses   = 0
        skipped_courses   = 0
        total_modules     = 0
        total_lessons     = 0
        total_quizzes     = 0
        total_questions   = 0
        total_choices     = 0

        for course_data in courses_data:
            title = course_data["title"]

            # ── Handle existing course ────────────────────────────────────────
            existing = Course.objects.filter(title=title).first()
            if existing:
                if options["force"]:
                    self.stdout.write(f"  --force: deleting existing course '{title}'")
                    existing.delete()
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  SKIPPED (already exists): {title}")
                    )
                    skipped_courses += 1
                    continue

            # ── Create Course ────────────────────────────────────────────────
            course = Course.objects.create(
                title=title,
                description=course_data.get("description", ""),
                is_published=course_data.get("is_published", True),
            )
            created_courses += 1
            self.stdout.write(f"  ✓ Course: {course.title}")

            # ── Modules ──────────────────────────────────────────────────────
            for mod_data in course_data.get("modules", []):
                module = Module.objects.create(
                    course=course,
                    title=mod_data["title"],
                    sequence_order=mod_data["sequence_order"],
                )
                total_modules += 1

                # ── Lessons ──────────────────────────────────────────────────
                for lesson_data in mod_data.get("lessons", []):
                    Lesson.objects.create(
                        module=module,
                        title=lesson_data["title"],
                        text_content=lesson_data.get("text_content") or "",
                        video_s3_url=lesson_data.get("video_s3_url") or None,
                        sequence_order=lesson_data["sequence_order"],
                        estimated_minutes=lesson_data.get("estimated_minutes", 20),
                    )
                    total_lessons += 1

                # ── Quiz (one per module, all questions merged) ────────────────
                quiz_data = mod_data.get("quiz")
                if quiz_data and quiz_data.get("questions"):
                    quiz = Quiz.objects.create(
                        module=module,
                        title=quiz_data["title"],
                        passing_threshold=quiz_data.get("passing_threshold", 70),
                    )
                    total_quizzes += 1

                    for q_data in quiz_data["questions"]:
                        question = Question.objects.create(
                            quiz=quiz,
                            question_text=q_data["question_text"],
                        )
                        total_questions += 1

                        for choice_data in q_data.get("choices", []):
                            AnswerChoice.objects.create(
                                question=question,
                                choice_text=choice_data["choice_text"],
                                is_correct=choice_data.get("is_correct", False),
                            )
                            total_choices += 1

                self.stdout.write(
                    f"    ↳ Module: {module.title} "
                    f"({len(mod_data.get('lessons', []))} lesson(s), "
                    f"{len(quiz_data.get('questions', [])) if quiz_data else 0} question(s))"
                )

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("── Seeding complete ─────────────────────"))
        self.stdout.write(f"  Courses created : {created_courses}")
        self.stdout.write(f"  Courses skipped : {skipped_courses}")
        self.stdout.write(f"  Modules         : {total_modules}")
        self.stdout.write(f"  Lessons         : {total_lessons}")
        self.stdout.write(f"  Quizzes         : {total_quizzes}")
        self.stdout.write(f"  Questions       : {total_questions}")
        self.stdout.write(f"  Answer choices  : {total_choices}")
        self.stdout.write(self.style.SUCCESS("─────────────────────────────────────────"))