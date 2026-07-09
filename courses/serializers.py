from rest_framework import serializers
from .models import Course, Module, Lesson
from django.core.exceptions import ObjectDoesNotExist
from progress.models import Enrollment
from .utils import calculate_progress


# Student serializers
class StudentLessonSerializer(serializers.ModelSerializer):
    """Student view: Enforces locks and strips content."""
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'text_content', 'video_s3_url', 'sequence_order', 'estimated_minutes', 'is_locked']

    def get_is_locked(self, obj):
        locked_modules = self.context.get('locked_modules', set())
        return obj.module_id in locked_modules

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('is_locked'):
            data['text_content'] = None
            data['video_s3_url'] = None
        return data

class StudentModuleSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'sequence_order', 'is_locked', 'lesson_count', 'lessons']

    def get_is_locked(self, obj):
        locked_modules = self.context.get('locked_modules', set())
        return obj.id in locked_modules

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_lessons(self, obj):
        locked_modules = self.context.get('locked_modules', set())
        lessons = obj.lessons.order_by('sequence_order')
        return StudentLessonSerializer(
            lessons, many=True, context={'locked_modules': locked_modules}
        ).data


class StudentCourseDetailSerializer(serializers.ModelSerializer):
    """Uses the StudentModuleSerializer (enforces locks)"""
    modules = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail_url',
            'modules', 'total_lessons', 'module_count',
            'is_enrolled', 'progress_percentage'
        ]

    def get_modules(self, obj):
        return StudentModuleSerializer(
            obj.modules.all(),
            many=True,
            context=self.context
        ).data

    def get_total_lessons(self, obj):
        return sum(len(m.lessons.all()) for m in obj.modules.all())

    def get_module_count(self, obj):
        return len(obj.modules.all())

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(student=request.user, course=obj).exists()

    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        is_enrolled = Enrollment.objects.filter(student=request.user, course=obj).exists()
        if not is_enrolled:
            return 0

        return calculate_progress(request.user, obj)

# shared serializers (student and admin)
class CourseListSerializer(serializers.ModelSerializer):
    total_lessons = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'thumbnail_url',
            'is_published',
            'created_at',
            'updated_at',
            'total_lessons',
            'module_count',
        ]

    def get_total_lessons(self, obj):
        return sum(len(m.lessons.all()) for m in obj.modules.all())

    def get_module_count(self, obj):
        return len(obj.modules.all())

# Admin serializers
class AdminLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'text_content',
            'video_s3_url',
            'sequence_order',
            'estimated_minutes',
        ]


class AdminModuleSerializer(serializers.ModelSerializer):
    lessons = AdminLessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id',
            'title',
            'sequence_order',
            'lessons',
            'lesson_count',
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class AdminCourseDetailSerializer(serializers.ModelSerializer):
    """Uses the AdminModuleSerializer (sees all content)"""
    modules = AdminModuleSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail_url',
            'is_published', 'created_at', 'updated_at',
            'modules', 'total_lessons', 'module_count'
        ]

    def get_total_lessons(self, obj):
        return sum(len(m.lessons.all()) for m in obj.modules.all())

    def get_module_count(self, obj):
        return len(obj.modules.all())


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'thumbnail_url',
            'is_published',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            'id',
            'title',
            'sequence_order',
        ]
        read_only_fields = ['id']


class LessonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'text_content',
            'video_s3_url',
            'sequence_order',
            'estimated_minutes',
        ]
        read_only_fields = ['id']