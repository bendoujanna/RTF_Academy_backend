from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certificate
from .serializers import CertificateSerializer


class MyCertificatesView(APIView):
    """
    GET /api/certificates/my/
    Returns all certificates earned by the authenticated student
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(
            student=request.user
        ).select_related('course').order_by('-issued_at')
        return Response(CertificateSerializer(certificates, many=True).data)


class CertificateVerifyView(APIView):
    """
    GET /api/certificates/verify/{code}/
    Public endpoint
    Used by employers or institutions to verify a certificate's authenticity
    """
    permission_classes = []
    authentication_classes = []

    def get(self, request, code):
        try:
            cert = Certificate.objects.select_related('student', 'course').get(
                verification_code=code
            )
            return Response({
                'valid': True,
                'student_name': cert.student.full_name,
                'course_title': cert.course.title,
                'issued_at': cert.issued_at,
                'verification_code': cert.verification_code,
            })
        except Certificate.DoesNotExist:
            return Response(
                {'valid': False, 'detail': 'Certificate not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class CertificateDownloadView(APIView):
    """
    GET /api/certificates/download/{id}/
    Returns the S3 URL for the certificate PDF.
    Returns 503 if S3/boto3 has not been configured yet.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, cert_id):
        try:
            cert = Certificate.objects.get(pk=cert_id, student=request.user)
        except Certificate.DoesNotExist:
            return Response(
                {'detail': 'Certificate not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not cert.pdf_s3_url:
            return Response(
                {
                    'detail': 'PDF generation is pending. AWS S3 configuration required.',
                    'verification_code': cert.verification_code,
                    'course': cert.course.title,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({'pdf_url': cert.pdf_s3_url})