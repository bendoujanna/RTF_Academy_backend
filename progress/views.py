from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Enrollment, LessonCompletion
from .serializers import EnrollmentSerializer
from courses.models import Course, Lesson
from courses.utils import get_locked_modules, calculate_progress, is_course_complete
from certificates.utils import generate_certificate
from django.db import transaction

class EnrollmentView(APIView):
    """
    GET  /api/enrollments/  — Returns all enrollments for the authenticated student.
    POST /api/enrollments/  — Enrolls the student in a course
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            student=request.user
        ).select_related('course').order_by('-enrolled_at')
        return Response(EnrollmentSerializer(enrollments, many=True).data)

    def post(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'detail': 'course_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(pk=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response(
                {'detail': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'progress_percentage': 0, 'is_completed': False}
        )

        if not created:
            return Response(
                {
                    'detail': 'Already enrolled.',
                    'enrollment': EnrollmentSerializer(enrollment).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )


class EnrollmentDetailView(APIView):
    """
    GET /api/enrollments/{course_id}/
    Returns enrollment status for a specific course
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            enrollment = Enrollment.objects.select_related('course').get(
                student=request.user, course_id=course_id
            )
            return Response(EnrollmentSerializer(enrollment).data)
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'Not enrolled in this course.'},
                status=status.HTTP_404_NOT_FOUND
            )


class LessonCompleteView(APIView):
    """
    POST /api/progress/lesson/
    Marks a lesson as complete for the authenticated student.
    Recalculates course progress. Triggers certificate generation if course hits 100%
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        if not lesson_id:
            return Response(
                {'detail': 'lesson_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.select_related('module__course').get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {'detail': 'Lesson not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        course = lesson.module.course
        student = request.user

        try:
            enrollment = Enrollment.objects.get(student=student, course=course)
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'You are not enrolled in this course.'},
                status=status.HTTP_403_FORBIDDEN
            )

        locked_modules = get_locked_modules(student, course)
        if lesson.module_id in locked_modules:
            return Response(
                {'detail': 'This lesson is locked. Complete the previous module first.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # safe to call multiple times
        LessonCompletion.objects.get_or_create(student=student, lesson=lesson)

        new_progress = calculate_progress(student, course)
        enrollment.progress_percentage = new_progress

        certificate_earned = None
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
            'lesson_id': str(lesson_id),
            'progress_percentage': new_progress,
            'course_completed': enrollment.is_completed,
        }
        if certificate_earned:
            response_data['certificate_earned'] = certificate_earned

        return Response(response_data, status=status.HTTP_200_OK)


class CourseProgressView(APIView):
    """
    GET /api/progress/course/{course_id}/
    Returns detailed progress metrics for a specific enrolled course
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            enrollment = Enrollment.objects.select_related('course').get(
                student=request.user, course_id=course_id
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'Not enrolled in this course.'},
                status=status.HTTP_404_NOT_FOUND
            )

        student = request.user
        course = enrollment.course

        completed_lesson_ids = list(
            LessonCompletion.objects.filter(
                student=student, lesson__module__course=course
            ).values_list('lesson_id', flat=True)
        )

        return Response({
            'course_id': str(course_id),
            'progress_percentage': enrollment.progress_percentage,
            'is_completed': enrollment.is_completed,
            'enrolled_at': enrollment.enrolled_at,
            'completed_lesson_ids': [str(lid) for lid in completed_lesson_ids],
        })