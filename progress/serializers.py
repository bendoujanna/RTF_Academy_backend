from rest_framework import serializers
from .models import Enrollment
from courses.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'course',
            'course_id',
            'progress_percentage',
            'is_completed',
            'enrolled_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'is_completed', 'enrolled_at']