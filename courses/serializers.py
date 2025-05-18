from rest_framework import serializers

from courses.models import Course, Lesson, Enrollment


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'is_published']
        extra_kwargs = {
            'slug': {'required': True},
            'title': {'required': True},
            'description': {'required': True},
        }

    def validate_slug(self, value):
        if Course.objects.filter(slug=value).exists():
            raise serializers.ValidationError('Course with this slug already exists.')
        return value


class GetCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'teacher', 'is_published', 'created_at', 'updated_at']
        read_only_fields = fields


class UpdateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_published']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'is_published': {'required': False},
        }


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'content', 'order', 'video_url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        course = attrs.get('course')
        order = attrs.get('order')
        if Lesson.objects.filter(course=course, order=order).exists():
            raise serializers.ValidationError({'order': 'Lesson order must be unique within a course.'})
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']
        read_only_fields = ['id', 'student', 'enrolled_at']
