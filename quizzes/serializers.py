from rest_framework import serializers
from .models import Quiz, Question, AnswerChoice,StudentAnswer
from progress.models import QuizAttempt

class AnswerChoiceStudentSerializer(serializers.ModelSerializer):
    """
    Student-facing answer choice serializer
    is_correct is excluded to prevent cheating
    """
    class Meta:
        model = AnswerChoice
        fields = ['id', 'choice_text']


class QuestionStudentSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choices']


class QuizStudentSerializer(serializers.ModelSerializer):
    questions = QuestionStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'passing_threshold', 'questions']


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'passed', 'attempted_at']