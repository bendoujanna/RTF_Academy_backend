from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsAdminRole
from .utils import get_locked_modules
from .models import Course, Module, Lesson
from .serializers import (
    CourseCreateUpdateSerializer,
    StudentCourseDetailSerializer,
    CourseListSerializer,
    StudentLessonSerializer,
    StudentModuleSerializer,
    AdminModuleSerializer,
    AdminLessonSerializer,
    AdminCourseDetailSerializer

)
from progress.models import Enrollment


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
