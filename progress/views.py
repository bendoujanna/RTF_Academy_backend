from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Handles student enrollments.
    GET /enrollments/ - List my enrollments
    POST /enrollments/ - Enroll in a course
    GET /enrollments/{course_id}/ - Get status for a specific course
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = 'course_id'

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')

        if not course_id:
            return Response({"error": "course ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            enrollment = Enrollment.objects.create(
                student=request.user,
                course_id=course_id
            )
            serializer = self.get_serializer(enrollment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "You are already enrolled in this course."},
                status=status.HTTP_409_CONFLICT
            )