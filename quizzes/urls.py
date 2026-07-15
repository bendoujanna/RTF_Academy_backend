from django.urls import path
from .views import (
    QuizDetailView,
    QuizSubmitView,
    QuizResultView,
    AdminModuleQuizCreateView,
    AdminQuizListView,
    AdminQuizDetailView,
    AdminQuizQuestionCreateView,
    AdminQuestionDetailView,
)

urlpatterns = [
    # student routes
    path('module/<uuid:module_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<uuid:quiz_id>/submit/', QuizSubmitView.as_view(), name='quiz-submit'),
    path('<uuid:quiz_id>/result/', QuizResultView.as_view(), name='quiz-result'),

    # admin routes
    path('admin/modules/<uuid:module_id>/quiz/', AdminModuleQuizCreateView.as_view(), name='admin-quiz-create'),
    path('admin/quizzes/', AdminQuizListView.as_view(), name='admin-quiz-list'),
    path('admin/quizzes/<uuid:pk>/', AdminQuizDetailView.as_view(), name='admin-quiz-detail'),
    path('admin/quizzes/<uuid:quiz_id>/questions/', AdminQuizQuestionCreateView.as_view(), name='admin-question-create'),
    path('admin/questions/<uuid:pk>/', AdminQuestionDetailView.as_view(), name='admin-question-detail'),
]