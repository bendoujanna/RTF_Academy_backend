from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from courses.models import Module
from users.permissions import IsAdminRole
from .models import Quiz, Question, AnswerChoice, StudentAnswer
from .serializers import (
    QuizStudentSerializer,
    QuizAttemptResultSerializer,
    AdminQuizDetailSerializer,
    AdminQuizListSerializer,
    QuizWriteSerializer,
    AdminQuestionSerializer,
    QuestionWriteSerializer,
)
from progress.models import Enrollment, QuizAttempt
from courses.utils import get_locked_modules, calculate_progress, is_course_complete
from certificates.utils import generate_certificate


class QuizDetailView(APIView):
    """
    GET /api/assessments/module/{module_id}/
    Returns the quiz for a specific module, without is_correct on any answer choice.
    Blocked if the module is locked or the student is not enrolled.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, module_id):
        try:
            quiz = Quiz.objects.select_related('module__course').get(module_id=module_id)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'No quiz found for this module.'},
                status=status.HTTP_404_NOT_FOUND
            )

        course = quiz.module.course
        student = request.user

        if not Enrollment.objects.filter(student=student, course=course).exists():
            return Response(
                {'detail': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locked_modules = get_locked_modules(student, course)
        if quiz.module_id in locked_modules:
            return Response(
                {'detail': 'This module is locked. Complete the previous module first.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(QuizStudentSerializer(quiz).data)


class QuizSubmitView(APIView):
    """
    POST /api/assessments/{quiz_id}/submit/
    Grades the submitted answers, records the attempt, and checks for course completion.
    Students may submit multiple times, retakes are allowed
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.prefetch_related(
                'questions__choices'
            ).select_related('module__course').get(pk=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {'detail': 'Quiz not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        course = quiz.module.course
        student = request.user

        try:
            enrollment = Enrollment.objects.get(student=student, course=course)
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locked_modules = get_locked_modules(student, course)
        if quiz.module_id in locked_modules:
            return Response(
                {'detail': 'This module is locked.'},
                status=status.HTTP_403_FORBIDDEN
            )

        raw_answers = request.data.get('answers', [])
        if not raw_answers:
            return Response(
                {'detail': 'answers list is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduplicate answers by question_id, keep last submission per question
        answer_map = {}
        for answer in raw_answers:
            q_id = answer.get('question_id')
            c_id = answer.get('choice_id')
            if q_id and c_id:
                answer_map[str(q_id)] = str(c_id)

        total_questions = quiz.questions.count()
        if total_questions == 0:
            return Response(
                {'detail': 'This quiz has no questions.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Grade answers
        correct_count = 0
        graded = []

        submitted_choice_ids = list(answer_map.values())

        selected_choices = AnswerChoice.objects.filter(
            id__in=submitted_choice_ids,
            question__quiz=quiz
        ).select_related('question')

        for choice in selected_choices:
            if choice.is_correct:
                correct_count += 1
            graded.append((choice.question, choice))

        score = int((correct_count / total_questions) * 100)
        passed = score >= quiz.passing_threshold

        # Record the attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score,
            passed=passed,
        )

        for question, choice in graded:
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=choice,
            )

        # If passed, recalculate progress and check for course completion
        certificate_earned = None
        if passed:
            new_progress = calculate_progress(student, course)
            enrollment.progress_percentage = new_progress

            if is_course_complete(student, course):
                enrollment.is_completed = True
                cert, created = generate_certificate(student, course)
                if created:
                    certificate_earned = {
                        'verification_code': cert.verification_code,
                        'issued_at': str(cert.issued_at),
                    }

            enrollment.save()

        response_data = {
            'attempt_id': str(attempt.id),
            'score': score,
            'passed': passed,
            'passing_threshold': quiz.passing_threshold,
            'correct_answers': correct_count,
            'total_questions': total_questions,
        }
        if certificate_earned:
            response_data['certificate_earned'] = certificate_earned

        return Response(response_data, status=status.HTTP_201_CREATED)


class QuizResultView(APIView):
    """
    GET /api/assessments/{quiz_id}/result/
    Returns all previous attempts for a quiz by the authenticated student, newest first
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        attempts = QuizAttempt.objects.filter(
            student=request.user, quiz_id=quiz_id
        ).order_by('-attempted_at')

        if not attempts.exists():
            return Response(
                {'detail': 'No attempts found for this quiz.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(QuizAttemptResultSerializer(attempts, many=True).data)


def _quiz_base_queryset():
    return Quiz.objects.select_related('module__course').prefetch_related(
        Prefetch('questions', queryset=Question.objects.prefetch_related('choices'))
    )


class AdminModuleQuizCreateView(APIView):
    """
    POST /api/assessments/admin/modules/{module_id}/quiz/
    Creates the quiz for a module. A module may have at most one quiz.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request, module_id):
        module = get_object_or_404(Module, pk=module_id)
        if Quiz.objects.filter(module=module).exists():
            return Response(
                {'detail': 'This module already has a quiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuizWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save(module=module)
        return Response(AdminQuizDetailSerializer(quiz).data, status=status.HTTP_201_CREATED)


class AdminQuizListView(generics.ListAPIView):
    """GET /api/assessments/admin/quizzes/"""
    serializer_class = AdminQuizListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = _quiz_base_queryset().order_by('module__course__title', 'module__sequence_order')


class AdminQuizDetailView(APIView):
    """
    GET/PUT/DELETE /api/assessments/admin/quizzes/{quiz_id}/
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def _get_quiz(self, pk):
        return get_object_or_404(_quiz_base_queryset(), pk=pk)

    def get(self, request, pk):
        return Response(AdminQuizDetailSerializer(self._get_quiz(pk)).data)

    def put(self, request, pk):
        quiz = self._get_quiz(pk)
        serializer = QuizWriteSerializer(quiz, data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(AdminQuizDetailSerializer(quiz).data)

    def delete(self, request, pk):
        quiz = self._get_quiz(pk)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminQuizQuestionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    @transaction.atomic
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        serializer = QuestionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(quiz=quiz)
        return Response(AdminQuestionSerializer(question).data, status=status.HTTP_201_CREATED)


class AdminQuestionDetailView(APIView):
    """
    PUT/DELETE /api/assessments/admin/questions/{question_id}/
    PUT replaces the question text and its full set of choices in one request.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def _get_question(self, pk):
        return get_object_or_404(
            Question.objects.select_related('quiz').prefetch_related('choices'), pk=pk
        )

    @transaction.atomic
    def put(self, request, pk):
        question = self._get_question(pk)
        serializer = QuestionWriteSerializer(question, data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response(AdminQuestionSerializer(question).data)

    def delete(self, request, pk):
        question = self._get_question(pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)