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
    

class CourseCreateUpdateSerializer(serializers.ModelSerializer):
   modules = ModuleSerializer(many=True, required=False)
  
   class Meta:
       model = Course
       fields = [
           'id',
           'title',
           'description',
           'thumbnail_url',
           'is_published',
           'modules',
       ]
       read_only_fields = ['id', 'created_at', 'updated_at']
  
   def create(self, validated_data):
       modules_data = validated_data.pop('modules', [])


       course = Course.objects.create(**validated_data)


       for module_data in modules_data:
           lessons_data = module_data.pop('lessons', [])


           module = Module.objects.create(course=course, **module_data)


           for lesson_data in lessons_data:
               Lesson.objects.create(module=module, **lesson_data)


       return course
  
   def update(self, instance, validated_data):
       modules_data = validated_data.pop('modules', None)


       for attr, value in validated_data.items():
           setattr(instance, attr, value)
       instance.save()


       if modules_data is not None:
           # Replacing nested modules keeps writes deterministic but resets nested IDs.
           instance.modules.all().delete()


           for module_data in modules_data:
               lessons_data = module_data.pop('lessons', [])
               module = Module.objects.create(course=instance, **module_data)


               for lesson_data in lessons_data:
                   Lesson.objects.create(module=module, **lesson_data)


       return instance
