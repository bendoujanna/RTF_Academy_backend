from django.urls import path

from .views import (
    AdminCourseDetailView,
    AdminCourseListCreateView,
    CourseDetailView,
    CourseListView,
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<uuid:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('admin/', AdminCourseListCreateView.as_view(), name='admin-course-list-create'),
    path('admin/<uuid:pk>/', AdminCourseDetailView.as_view(), name='admin-course-detail'),
]