from django.db.models import Avg, Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from certificates.models import Certificate
from progress.models import Enrollment, LessonCompletion, QuizAttempt
from users.permissions import IsAdminRole

from quizzes.models import Question, Quiz
from users.models import UserProfile

from .utils import get_locked_modules
from .models import Course, Lesson, Module
from .serializers import (
    AdminCourseDetailSerializer,
    AdminLessonSerializer,
    AdminModuleSerializer,
    CourseCreateUpdateSerializer,
    CourseListSerializer,
    LessonWriteSerializer,
    ModuleWriteSerializer,
    CourseListSerializer,
    StudentCourseDetailSerializer,
    StudentLessonSerializer,
    StudentModuleSerializer,
)


def _is_admin(user):
    return bool(user and user.is_authenticated and getattr(user, 'role', None) == 'Admin')


def _course_base_queryset():
    return Course.objects.prefetch_related(
        Prefetch(
            'modules',
            queryset=Module.objects.prefetch_related('lessons').order_by('sequence_order'),
        )
    )


class CourseListView(generics.ListAPIView):
    """List published courses for authenticated users."""

    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return _course_base_queryset().filter(is_published=True).order_by('-created_at')


class CourseDetailView(generics.RetrieveAPIView):
    """Retrieve a published course including modules and lessons."""

    serializer_class = StudentCourseDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return _course_base_queryset().filter(is_published=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        request = context.get('request')

        try:
            course = self.get_object()
        except AssertionError:
            return context

        if request and request.user.is_authenticated:
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                context['locked_modules'] = get_locked_modules(request.user, course)
                return context

        context['locked_modules'] = set(course.modules.values_list('id', flat=True))

        return context


class CourseModuleCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        serializer = ModuleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        module = serializer.save(course=course)
        return Response(AdminModuleSerializer(module).data, status=status.HTTP_201_CREATED)


class ModuleDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def _get_module(self, module_id):
        return get_object_or_404(Module.objects.select_related('course').prefetch_related('lessons'), pk=module_id)

    def put(self, request, pk):
        module = self._get_module(pk)
        serializer = ModuleWriteSerializer(module, data=request.data)
        serializer.is_valid(raise_exception=True)
        module = serializer.save()
        return Response(AdminModuleSerializer(module).data)

    def delete(self, request, pk):
        module = self._get_module(pk)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ModuleLessonCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, module_id):
        module = get_object_or_404(Module, pk=module_id)
        serializer = LessonWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save(module=module)
        return Response(AdminLessonSerializer(lesson).data, status=status.HTTP_201_CREATED)

class StudentLessonDetailView(APIView):
    """
    GET /api/lessons/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            lesson = Lesson.objects.select_related('module__course').get(pk=pk)
        except Lesson.DoesNotExist:
            return Response(
                {'detail': 'Lesson not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        course = lesson.module.course
        student = request.user

        if not Enrollment.objects.filter(student=student, course=course).exists():
            return Response(
                {'detail': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locked_modules = get_locked_modules(student, course)

        if lesson.module.id in locked_modules:
            return Response(
                {'detail': 'This module is currently locked. Please complete previous modules.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StudentLessonSerializer(
            lesson, context={'locked_modules': locked_modules}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        if not _is_admin(request.user):
            return Response({'detail': 'Admin privileges required.'}, status=status.HTTP_403_FORBIDDEN)

        lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk)
        serializer = LessonWriteSerializer(lesson, data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return Response(AdminLessonSerializer(lesson).data)

    def delete(self, request, pk):
        if not _is_admin(request.user):
            return Response({'detail': 'Admin privileges required.'}, status=status.HTTP_403_FORBIDDEN)

        lesson = get_object_or_404(Lesson, pk=pk)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminCourseListCreateView(generics.ListCreateAPIView):
    """Admin endpoint to list and create courses."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return _course_base_queryset().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer


class AdminCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin endpoint to retrieve, update, or delete a course."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return _course_base_queryset()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateUpdateSerializer
        return AdminCourseDetailSerializer


class AdminCoursePublishView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        course = get_object_or_404(Course.objects.prefetch_related('modules__lessons'), pk=pk)
        course.is_published = True
        course.save(update_fields=['is_published', 'updated_at'])
        return Response(AdminCourseDetailSerializer(course, context=self.get_serializer_context(request)).data)

    def get_serializer_context(self, request):
        return {'request': request}


class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()
        total_enrollments = Enrollment.objects.count()
        completed_enrollments = Enrollment.objects.filter(is_completed=True).count()

        stats = {
            'courses': {
                'total': total_courses,
                'published': published_courses,
                'draft': total_courses - published_courses,
            },
            'content': {
                'modules': Module.objects.count(),
                'lessons': Lesson.objects.count(),
                'quizzes': Quiz.objects.count(),
                'questions': Question.objects.count(),
            },
            'learners': {
                'students': UserProfile.objects.filter(role='Student').count(),
                'enrollments': total_enrollments,
                'completed_enrollments': completed_enrollments,
                'lesson_completions': LessonCompletion.objects.count(),
                'certificates_issued': Certificate.objects.count(),
            },
            'assessments': {
                'quiz_attempts': QuizAttempt.objects.count(),
                'passed_attempts': QuizAttempt.objects.filter(passed=True).count(),
                'average_score': QuizAttempt.objects.aggregate(avg_score=Avg('score'))['avg_score'] or 0,
            },
        }

        return Response(stats)


class AdminEnrollmentReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        courses = (
            Course.objects.annotate(
                enrollment_count=Count('enrollments', distinct=True),
                completed_enrollment_count=Count(
                    'enrollments',
                    filter=Q(enrollments__is_completed=True),
                    distinct=True,
                ),
                certificate_count=Count('certificates', distinct=True),
                average_progress=Avg('enrollments__progress_percentage'),
            )
            .order_by('-enrollment_count', 'title')
        )

        summary = {
            'enrollments': Enrollment.objects.count(),
            'completed_enrollments': Enrollment.objects.filter(is_completed=True).count(),
            'average_progress': Enrollment.objects.aggregate(avg_progress=Avg('progress_percentage'))['avg_progress'] or 0,
        }

        results = []
        for course in courses:
            results.append(
                {
                    'course_id': course.id,
                    'title': course.title,
                    'is_published': course.is_published,
                    'enrollments': course.enrollment_count,
                    'completed_enrollments': course.completed_enrollment_count,
                    'average_progress': round(course.average_progress or 0, 2),
                    'certificates_issued': course.certificate_count,
                }
            )

        return Response({'summary': summary, 'results': results})
