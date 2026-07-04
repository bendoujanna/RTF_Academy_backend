from rest_framework import serializers
from .models import Course, Module, Lesson


class LessonSerializer(serializers.ModelSerializer):
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


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
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
        return Lesson.objects.filter(module__course=obj).count()
    
    def get_module_count(self, obj):
        return obj.modules.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    total_lessons = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()

    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
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
            'modules',
            'total_lessons',
            'module_count',
            'is_enrolled',
            'progress_percentage',
        ]
    
    def get_total_lessons(self, obj):
        return Lesson.objects.filter(module__course=obj).count()
    
    def get_module_count(self, obj):
        return obj.modules.count()
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return False
        return False
    
    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return 0
        return 0