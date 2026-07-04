from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.permissions import IsAdminRole

from .models import Course, Module
from .serializers import (
    CourseCreateUpdateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
)


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

    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return _course_base_queryset().filter(is_published=True)


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
        return CourseDetailSerializer
