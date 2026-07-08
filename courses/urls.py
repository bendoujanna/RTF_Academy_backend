from django.urls import path

from .views import (
    AdminCourseDetailView,
    AdminCourseListCreateView,
    CourseDetailView,
    CourseListView,
    StudentLessonDetailView
)

urlpatterns = [

    # student routes
    path('', CourseListView.as_view(), name='course-list'),
    path('<uuid:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('lessons/<uuid:pk>/', StudentLessonDetailView.as_view(), name='lesson-detail'),

    # admin routes
    path('admin/', AdminCourseListCreateView.as_view(), name='admin-course-list-create'),
    path('admin/<uuid:pk>/', AdminCourseDetailView.as_view(), name='admin-course-detail'),
]