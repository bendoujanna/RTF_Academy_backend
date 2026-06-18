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


        course_1, _ = Course.objects.get_or_create(
            title="Digital Literacy for Refugee Youth",
            defaults={
                'description': "Master essential computer, internet, and productivity skills.",
                'thumbnail_url': "https://images.unsplash.com/photo-1555066931-4365d14bab8c",
                'is_published': True
            }
        )

        c1_mod1, _ = Module.objects.get_or_create(
            course=course_1, title="Module 1: Introduction to Computers", sequence_order=1
        )
        c1_lesson1, _ = Lesson.objects.get_or_create(
            module=c1_mod1, title="What is a Computer?", sequence_order=1,
            defaults={
                'text_content': "A computer is an electronic device that processes data.",
                'estimated_minutes': 15
            }
        )
        c1_quiz1, _ = Quiz.objects.get_or_create(
            module=c1_mod1,
            defaults={'title': "Computer Basics Quiz", 'passing_threshold': 80}
        )
        c1_q1, _ = Question.objects.get_or_create(
            quiz=c1_quiz1, question_text="Which of the following is computer hardware?"
        )
        c1_q1_correct, _ = AnswerChoice.objects.get_or_create(
            question=c1_q1, choice_text="Keyboard", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c1_q1, choice_text="Web Browser", defaults={'is_correct': False}
        )

        c1_mod2, _ = Module.objects.get_or_create(
            course=course_1, title="Module 2: Internet & Web Browsing", sequence_order=2
        )
        c1_lesson2, _ = Lesson.objects.get_or_create(
            module=c1_mod2, title="Using a Web Browser", sequence_order=1,
            defaults={
                'text_content': "A web browser is software used to access and navigate the internet.",
                'estimated_minutes': 20
            }
        )
        c1_quiz2, _ = Quiz.objects.get_or_create(
            module=c1_mod2,
            defaults={'title': "Internet Basics Quiz", 'passing_threshold': 80}
        )
        c1_q2, _ = Question.objects.get_or_create(
            quiz=c1_quiz2, question_text="What does URL stand for?"
        )
        c1_q2_correct, _ = AnswerChoice.objects.get_or_create(
            question=c1_q2, choice_text="Uniform Resource Locator", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c1_q2, choice_text="Universal Reading Link", defaults={'is_correct': False}
        )


        c1_mod3, _ = Module.objects.get_or_create(
            course=course_1, title="Module 3: Email & Communication", sequence_order=3
        )
        c1_lesson3, _ = Lesson.objects.get_or_create(
            module=c1_mod3, title="Creating an Email Account", sequence_order=1,
            defaults={
                'text_content': "Email is an electronic method of exchanging messages over the internet.",
                'estimated_minutes': 20
            }
        )
        c1_quiz3, _ = Quiz.objects.get_or_create(
            module=c1_mod3,
            defaults={'title': "Email Fundamentals Quiz", 'passing_threshold': 80}
        )
        c1_q3, _ = Question.objects.get_or_create(
            quiz=c1_quiz3, question_text="Which of these is a valid email address format?"
        )
        c1_q3_correct, _ = AnswerChoice.objects.get_or_create(
            question=c1_q3, choice_text="user@example.com", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c1_q3, choice_text="user.example.com", defaults={'is_correct': False}
        )


        for lesson, quiz, correct_choice in [
            (c1_lesson1, c1_quiz1, c1_q1_correct),
            (c1_lesson2, c1_quiz2, c1_q2_correct),
            (c1_lesson3, c1_quiz3, c1_q3_correct),
        ]:
            LessonCompletion.objects.get_or_create(student=student_user, lesson=lesson)
            attempt, _ = QuizAttempt.objects.get_or_create(
                student=student_user, quiz=quiz,
                defaults={'score': 100, 'passed': True}
            )
            StudentAnswer.objects.get_or_create(
                attempt=attempt, question=correct_choice.question,
                defaults={'selected_choice': correct_choice}
            )

        Enrollment.objects.get_or_create(
            student=student_user, course=course_1,
            defaults={'progress_percentage': 100, 'is_completed': True}
        )

        Certificate.objects.get_or_create(
            student=student_user, course=course_1,
            defaults={
                'verification_code': 'RTF-CERT-889900',
                'pdf_s3_url': 'https://s3.amazonaws.com/rtf-certs/cert-digital-literacy.pdf'
            }
        )

        course_2, _ = Course.objects.get_or_create(
            title="English Language Essentials",
            defaults={
                'description': "Build reading, writing, and conversational skills in English.",
                'thumbnail_url': "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
                'is_published': True
            }
        )

        c2_mod1, _ = Module.objects.get_or_create(
            course=course_2, title="Module 1: Greetings & Introductions", sequence_order=1
        )
        c2_lesson1, _ = Lesson.objects.get_or_create(
            module=c2_mod1, title="Common Greetings", sequence_order=1,
            defaults={
                'text_content': "Learn everyday English greetings used in professional and social contexts.",
                'estimated_minutes': 20
            }
        )
        c2_quiz1, _ = Quiz.objects.get_or_create(
            module=c2_mod1,
            defaults={'title': "Greetings & Introductions Quiz", 'passing_threshold': 80}
        )
        c2_q1, _ = Question.objects.get_or_create(
            quiz=c2_quiz1, question_text="Which phrase is the most appropriate formal greeting?"
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q1, choice_text="Good morning, how do you do?", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q1, choice_text="Hey, what's up?", defaults={'is_correct': False}
        )


        c2_mod2, _ = Module.objects.get_or_create(
            course=course_2, title="Module 2: Everyday Vocabulary", sequence_order=2
        )
        c2_lesson2, _ = Lesson.objects.get_or_create(
            module=c2_mod2, title="Family & Relationships", sequence_order=1,
            defaults={
                'text_content': "Learn vocabulary related to family members and personal relationships.",
                'estimated_minutes': 20
            }
        )
        c2_quiz2, _ = Quiz.objects.get_or_create(
            module=c2_mod2,
            defaults={'title': "Everyday Vocabulary Quiz", 'passing_threshold': 80}
        )
        c2_q2, _ = Question.objects.get_or_create(
            quiz=c2_quiz2, question_text="Which word describes a person's mother or father?"
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q2, choice_text="Parent", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q2, choice_text="Sibling", defaults={'is_correct': False}
        )

        c2_mod3, _ = Module.objects.get_or_create(
            course=course_2, title="Module 3: Reading & Writing", sequence_order=3
        )
        c2_lesson3, _ = Lesson.objects.get_or_create(
            module=c2_mod3, title="Reading Short Passages", sequence_order=1,
            defaults={
                'text_content': "Practice reading short English passages and identifying the main idea.",
                'estimated_minutes': 25
            }
        )
        c2_quiz3, _ = Quiz.objects.get_or_create(
            module=c2_mod3,
            defaults={'title': "Reading Comprehension Quiz", 'passing_threshold': 80}
        )
        c2_q3, _ = Question.objects.get_or_create(
            quiz=c2_quiz3, question_text="What is the purpose of a topic sentence?"
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q3, choice_text="To introduce the main idea of a paragraph", defaults={'is_correct': True}
        )
        AnswerChoice.objects.get_or_create(
            question=c2_q3, choice_text="To conclude the paragraph", defaults={'is_correct': False}
        )

        LessonCompletion.objects.get_or_create(student=student_user, lesson=c2_lesson1)

        Enrollment.objects.get_or_create(
            student=student_user, course=course_2,
            defaults={'progress_percentage': 33, 'is_completed': False}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the complete RTF Academy Database.'))