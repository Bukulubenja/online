from rest_framework import serializers

from enrollments.models import LessonProgress

from .models import Course, Lesson, Module


class LessonSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'video_url', 'pdf', 'content', 'completed']

    def get_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Lesson ids are globally unique, so one query per request (cached on the
        # shared context dict) covers every course/module/lesson being serialized.
        completed_ids = self.context.get('_completed_lesson_ids')
        if completed_ids is None:
            completed_ids = set(
                LessonProgress.objects.filter(enrollment__student=request.user).values_list('lesson_id', flat=True)
            )
            self.context['_completed_lesson_ids'] = completed_ids
        return obj.id in completed_ids


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lessons']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'level', 'level_display', 'description', 'thumbnail',
            'price', 'instructor', 'is_published', 'modules',
        ]

    def get_instructor(self, obj):
        if obj.instructor is None:
            return None
        return obj.instructor.get_full_name() or obj.instructor.username
