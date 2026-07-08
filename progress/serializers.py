from rest_framework import serializers
from .models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'course',
            'course_title',
            'progress_percentage',
            'enrolled_at',
            'is_completed'
        ]
        read_only_fields = ['id', 'progress_percentage', 'enrolled_at', 'is_completed']