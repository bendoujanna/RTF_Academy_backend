import uuid
from certificates.models import Certificate


def generate_certificate(student, course):
    """
    Generates a certificate for a student who has completed a course.
    Idempotent, returns the existing certificate if one already exists.
    """
    existing = Certificate.objects.filter(student=student, course=course).first()
    if existing:
        return existing, False

    verification_code = (
        f"RTF-{course.created_at.year}-CERT-{uuid.uuid4().hex[:8].upper()}"
    )

    certificate = Certificate.objects.create(
        student=student,
        course=course,
        verification_code=verification_code,
        pdf_s3_url=None,
    )

    return certificate, True