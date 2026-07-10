from rest_framework import serializers
from .models import Certificate
from courses.serializers import CourseListSerializer


class CertificateSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'course', 'verification_code', 'pdf_s3_url', 'issued_at']