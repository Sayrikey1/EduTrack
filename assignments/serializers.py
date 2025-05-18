from rest_framework import serializers

from assignments.models import Assignment, Submission


class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date']
        extra_kwargs = {
            'course': {'required': True},
            'title': {'required': True},
            'description': {'required': True},
            'due_date': {'required': True},
        }


class GetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'due_date', 'created_at', 'updated_at']
        read_only_fields = fields


class UpdateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'due_date': {'required': False},
        }


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'content', 'submitted_at', 'status', 'grade', 'feedback']
        read_only_fields = ['id', 'student', 'submitted_at', 'status']