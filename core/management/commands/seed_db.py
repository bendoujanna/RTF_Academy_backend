from django.core.management.base import BaseCommand
from users.models import UserProfile
from courses.models import Course, Module, Lesson
from quizzes.models import Quiz, Question, AnswerChoice, StudentAnswer
from progress.models import Enrollment, LessonCompletion, QuizAttempt
from certificates.models import Certificate


class Command(BaseCommand):
    help = 'Seeds the PostgreSQL database with a complete RTF Academy test scenario.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Planting master seed data...")

        # identity
        admin_user = UserProfile.objects.filter(email="admin@rtfacademy.com").first()
        if not admin_user:
            admin_user = UserProfile.objects.create_user(
                uid='ADMIN_UID_123', email="admin@rtfacademy.com",
                full_name='RTF Admin', role='Admin'
            )

        student_user = UserProfile.objects.filter(email="student@rtfacademy.com").first()
        if not student_user:
            student_user = UserProfile.objects.create_user(
                uid='STUDENT_UID_456', email="student@rtfacademy.com",
                full_name='Test Student', role='Student'
            )

        # content
        course, _ = Course.objects.get_or_create(
            title="Digital Literacy for Refugee Youth",
            defaults={
                'description': "Master essential computer, internet, and productivity skills.",
                'thumbnail_url': "https://images.unsplash.com/photo-1555066931-4365d14bab8c",
                'is_published': True
            }
        )

        module_1, _ = Module.objects.get_or_create(
            course=course, title="Module 1: Introduction to Computers", sequence_order=1
        )

        lesson_1, _ = Lesson.objects.get_or_create(
            module=module_1, title="What is a Computer?", sequence_order=1,
            defaults={'text_content': "A computer is an electronic device that processes data.", 'estimated_minutes': 15}
        )

        # assessment
        quiz, _ = Quiz.objects.get_or_create(
            module=module_1, defaults={'title': "Computer Basics Quiz", 'passing_threshold': 80}
        )

        q1, _ = Question.objects.get_or_create(quiz=quiz, question_text="Which of the following is computer hardware?")

        q1_correct, _ = AnswerChoice.objects.get_or_create(
            question=q1, choice_text="Keyboard", defaults={'is_correct': True}
        )
        q1_wrong, _ = AnswerChoice.objects.get_or_create(
            question=q1, choice_text="Web Browser", defaults={'is_correct': False}
        )

        # progress
        attempt, _ = QuizAttempt.objects.get_or_create(
            student=student_user, quiz=quiz, defaults={'score': 100, 'passed': True}
        )

        StudentAnswer.objects.get_or_create(
            attempt=attempt, question=q1, defaults={'selected_choice': q1_correct}
        )

        LessonCompletion.objects.get_or_create(student=student_user, lesson=lesson_1)

        enrollment, _ = Enrollment.objects.get_or_create(
            student=student_user, course=course,
            defaults={'progress_percentage': 100, 'is_completed': True}
        )

        Certificate.objects.get_or_create(
            student=student_user, course=course,
            defaults={'verification_code': 'RTF-CERT-889900', 'pdf_s3_url': 'https://s3.amazonaws.com/cert.pdf'}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the complete RTF Academy Database!'))