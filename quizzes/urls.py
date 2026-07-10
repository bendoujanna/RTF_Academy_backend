from django.urls import path
from .views import QuizDetailView, QuizSubmitView, QuizResultView

urlpatterns = [
    path('module/<uuid:module_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<uuid:quiz_id>/submit/', QuizSubmitView.as_view(), name='quiz-submit'),
    path('<uuid:quiz_id>/result/', QuizResultView.as_view(), name='quiz-result'),
]