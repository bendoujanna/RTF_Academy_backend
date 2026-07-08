from django.contrib import admin

from progress.models import QuizAttempt
from .models import Quiz, Question, AnswerChoice, StudentAnswer

admin.site.register([Quiz, Question, AnswerChoice, StudentAnswer])
