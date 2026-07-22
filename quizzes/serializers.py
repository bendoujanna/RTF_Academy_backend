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


# Admin serializers (full CRUD, includes is_correct)
class AdminAnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'choice_text', 'is_correct']


class AdminQuestionSerializer(serializers.ModelSerializer):
    choices = AdminAnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choices']


class AdminQuizDetailSerializer(serializers.ModelSerializer):
    """Full quiz view for admins, including correct answers."""
    questions = AdminQuestionSerializer(many=True, read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_id = serializers.UUIDField(source='module.course_id', read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'passing_threshold', 'module', 'module_title', 'course_id', 'questions']
        read_only_fields = ['id', 'module']


class AdminQuizListSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'passing_threshold', 'module', 'module_title', 'question_count']

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'passing_threshold']
        read_only_fields = ['id']


class AnswerChoiceNestedWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'choice_text', 'is_correct']
        read_only_fields = ['id']


class QuestionWriteSerializer(serializers.ModelSerializer):
    """
    Writable nested serializer: a question and all of its choices are
    created/replaced together in one request.
    """
    choices = AnswerChoiceNestedWriteSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choices']
        read_only_fields = ['id']

    def validate_choices(self, value):
        if not value:
            raise serializers.ValidationError('At least one choice is required.')
        if not any(choice.get('is_correct') for choice in value):
            raise serializers.ValidationError('At least one choice must be marked as correct.')
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        AnswerChoice.objects.bulk_create([
            AnswerChoice(question=question, **choice) for choice in choices_data
        ])
        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)
        instance.question_text = validated_data.get('question_text', instance.question_text)
        instance.save()

        if choices_data is not None:
            instance.choices.all().delete()
            AnswerChoice.objects.bulk_create([
                AnswerChoice(question=instance, **choice) for choice in choices_data
            ])
        return instance