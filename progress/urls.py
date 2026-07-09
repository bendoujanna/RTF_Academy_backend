from django.urls import path
from .views import EnrollmentView, EnrollmentDetailView, LessonCompleteView, CourseProgressView

urlpatterns = [
    path('enrollments/', EnrollmentView.as_view(), name='enrollments-list-create'),
    path('enrollments/<uuid:course_id>/', EnrollmentDetailView.as_view(), name='enrollments-detail'),
    path('lesson/', LessonCompleteView.as_view(), name='lesson-complete'),
    path('course/<uuid:course_id>/', CourseProgressView.as_view(), name='course-progress'),
]