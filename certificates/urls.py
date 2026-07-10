from django.urls import path
from .views import MyCertificatesView, CertificateVerifyView, CertificateDownloadView

urlpatterns = [
    path('my/', MyCertificatesView.as_view(), name='my-certificates'),
    path('verify/<str:code>/', CertificateVerifyView.as_view(), name='certificate-verify'),
    path('download/<uuid:cert_id>/', CertificateDownloadView.as_view(), name='certificate-download'),
]