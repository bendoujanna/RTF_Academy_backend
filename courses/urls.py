from django.urls import path

from .views import (
    AdminCoursePublishView,
    AdminEnrollmentReportView,
    AdminStatsView,
    AdminCourseDetailView,
    AdminCourseListCreateView,
    CourseModuleCreateView,
    CourseDetailView,
    CourseListView,
    ModuleDetailView,
    ModuleLessonCreateView,
    StudentLessonDetailView
)

urlpatterns = [

    # student routes
    path('', CourseListView.as_view(), name='course-list'),
    path('<uuid:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('<uuid:course_id>/modules/', CourseModuleCreateView.as_view(), name='course-module-create'),
    path('modules/<uuid:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<uuid:module_id>/lessons/', ModuleLessonCreateView.as_view(), name='module-lesson-create'),
    path('lessons/<uuid:pk>/', StudentLessonDetailView.as_view(), name='lesson-detail'),

    # admin routes
    path('admin/', AdminCourseListCreateView.as_view(), name='admin-course-list-create'),
    path('admin/<uuid:pk>/', AdminCourseDetailView.as_view(), name='admin-course-detail'),
    path('admin/courses/<uuid:pk>/publish/', AdminCoursePublishView.as_view(), name='admin-course-publish'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/enrollments/report/', AdminEnrollmentReportView.as_view(), name='admin-enrollments-report'),
]