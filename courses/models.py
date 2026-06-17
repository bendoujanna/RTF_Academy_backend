from django.db import models
import uuid

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    sequence_order = models.IntegerField(default=1) # To order modules 1, 2, 3...

    class Meta:
        ordering = ['sequence_order'] # Always fetch them in the correct order

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    text_content = models.TextField(blank=True, null=True)
    video_s3_url = models.URLField(blank=True, null=True)
    sequence_order = models.IntegerField(default=1)
    estimated_minutes = models.IntegerField(default=10)

    class Meta:
        ordering = ['sequence_order']

    def __str__(self):
        return self.title