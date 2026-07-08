from django.core.exceptions import ObjectDoesNotExist

def get_locked_modules(student, course):
    """
    Returns a set of module IDs that are locked for a student in a course.

    Rules:
    - Module 1 is always unlocked for enrolled students.
    - Module N is locked if Module N-1 is not complete.
    - A module is complete when ALL its lessons are done AND its quiz is passed.
    - If a module has no quiz, only lesson completion is required.
    """
    from progress.models import LessonCompletion, QuizAttempt

    modules = list(course.modules.order_by('sequence_order'))
    locked_modules = set()

    for i, module in enumerate(modules):
        if i == 0:
            continue

        prev_module = modules[i - 1]

        prev_lesson_ids = set(prev_module.lessons.values_list('id', flat=True))
        completed_lesson_ids = set(
            LessonCompletion.objects.filter(
                student=student, lesson__module=prev_module
            ).values_list('lesson_id', flat=True)
        )
        if len(prev_lesson_ids) == 0:
            all_lessons_done = True
        else:
            all_lessons_done = (prev_lesson_ids == completed_lesson_ids)

        quiz_passed = True
        try:
            quiz = prev_module.quiz
            quiz_passed = QuizAttempt.objects.filter(
                student=student, quiz=quiz, passed=True
            ).exists()
        except ObjectDoesNotExist:
            quiz_passed = True

        if not (all_lessons_done and quiz_passed):
            for j in range(i, len(modules)):
                locked_modules.add(modules[j].id)
            break

    return locked_modules


def calculate_progress(student, course):
    """
    Progress = (completed_lessons + passed_quizzes) / (total_lessons + total_quizzes) * 100
    Passing a quiz is a requirement and counts toward progress alongside lessons.
    """
    from progress.models import LessonCompletion, QuizAttempt
    from courses.models import Lesson, Module

    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonCompletion.objects.filter(
        student=student, lesson__module__course=course
    ).count()

    # Bug fix: use filter(quiz__isnull=False) instead of exclude(quiz__isnull=True)
    # to avoid Django's known quirk with exclude() + null checks on reverse relations
    modules_with_quiz = list(
        Module.objects.filter(course=course, quiz__isnull=False)
    )
    total_quizzes = len(modules_with_quiz)
    passed_quizzes = sum(
        1 for m in modules_with_quiz
        if QuizAttempt.objects.filter(
            student=student, quiz=m.quiz, passed=True
        ).exists()
    )

    total = total_lessons + total_quizzes
    if total == 0:
        return 0

    return int((completed_lessons + passed_quizzes) / total * 100)


def is_course_complete(student, course):
    return calculate_progress(student, course) == 100