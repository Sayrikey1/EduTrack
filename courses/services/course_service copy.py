import logging
from typing import Any, Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from accounts.models import User, UserTypes
from courses.models import Course, Lesson, Enrollment
from courses.serializers import (
    CreateCourseSerializer, GetCourseSerializer,
    UpdateCourseSerializer, LessonSerializer, EnrollmentSerializer
)
from services.log import AppLogger
from services.pagination import ServicePaginationMixin

logger = logging.getLogger(__name__)

# Cache key constant
def _courses_cache_key() -> str:
    return "published_courses_list"


class CourseService(ServicePaginationMixin):
    def __init__(self, request):
        self.request = request
        self.auth_user: User = request.user

    # ------------------------------------
    # Helper methods
    # ------------------------------------
    def _get_teacher(self) -> Tuple[Optional[Any], Optional[str]]:
        if not self.auth_user.is_authenticated:
            return None, "Authentication required."
        if self.auth_user.user_type != UserTypes.teacher:
            return None, "Only teachers can manage courses."
        return self.auth_user, None

    @staticmethod
    def _get_course(pk: str) -> Tuple[Optional[Course], Optional[str]]:
        if not pk:
            return None, "Course ID not provided."
        try:
            return Course.objects.get(id=pk), None
        except Course.DoesNotExist:
            return None, "Course not found."

    # ------------------------------------
    # Course methods
    # ------------------------------------
    def list_courses(self) -> Tuple[List[Dict[str, Any]], None]:
        qs = Course.objects.filter(is_published=True)
        data = self.paginate(qs, GetCourseSerializer, self.request)
        return data, None

    def create_course(self, validated_data):
        teacher, error = self._get_teacher()
        if error:
            return None, error
    
        serializer = CreateCourseSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
    
        course = serializer.save(teacher=teacher)
    
        # invalidate cache
        cache.delete(_courses_cache_key())
    
        return GetCourseSerializer(course).data, None


    def get_course_detail(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        """
        Retrieve a course's details, cached per course ID.
        """
        cache_key = f"course_detail_{pk}"
        data = cache.get(cache_key)
        if data is None:
            course, error = self._get_course(pk)
            if error:
                return None, error
            data = GetCourseSerializer(course).data
            cache.set(cache_key, data, timeout=300)  # cache for 5 minutes
        return data, None


    def update_course(self, pk: str, validated_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error
        course, error = self._get_course(pk)
        if error:
            return None, error
        if course.teacher != teacher:
            return None, "Permission denied."
        serializer = UpdateCourseSerializer(course, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        # Invalidate cache on update
        cache.delete(_courses_cache_key())
        return GetCourseSerializer(updated).data, None

    def delete_course(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error
        course, error = self._get_course(pk)
        if error:
            return None, error
        if course.teacher != teacher:
            return None, "Permission denied."
        course.delete()
        # Invalidate cache on delete
        cache.delete(_courses_cache_key())
        return {"message": "Course deleted successfully."}, None

    # ------------------------------------
    # Enrollment methods
    # ------------------------------------
    def enroll(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        course, error = self._get_course(pk)
        if error:
            return None, error
        student = self.auth_user
        if student.user_type != UserTypes.student:
            return None, "Only students can enroll."
        enrollment, created = Enrollment.objects.get_or_create(
            student=student, course=course
        )
        serializer = EnrollmentSerializer(enrollment)
        return serializer.data, None

    def list_enrollments(self) -> Tuple[List[Dict[str, Any]], None]:
        qs = (Enrollment.objects
                    .filter(course__teacher=self.auth_user)
                    if self.auth_user.user_type == UserTypes.teacher
                    else Enrollment.objects.filter(student=self.auth_user))
        data = self.paginate(qs, EnrollmentSerializer, self.request)
        return data, None

    # ------------------------------------
    # Lesson methods
    # ------------------------------------
    def list_lessons(
        self, 
        course_pk: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        course, error = self._get_course(course_pk)
        if error:
            return [], error

        lessons_qs = course.lessons.all()
        data = self.paginate(
            lessons_qs,
            LessonSerializer,
            self.request,
        )
        return data, None

    def add_lesson(self, validated_data: Dict[str, Any], **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error
        
        course_pk = kwargs.get("pk")
        if not course_pk:
            return None, "Course ID not provided."
        course, error = self._get_course(course_pk)
        if error:
            return None, error
        if course.teacher != teacher:
            return None, "Permission denied."
        validated_data['course'] = course.id
        serializer = LessonSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return LessonSerializer(lesson).data, None

    def delete_lesson(self, course_pk: str, lesson_pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error
        lesson = Lesson.objects.filter(id=lesson_pk, course_id=course_pk).first()
        if not lesson:
            return None, "Lesson not found."
        if lesson.course.teacher != teacher:
            return None, "Permission denied."
        lesson.delete()
        return {"message": "Lesson deleted successfully."}, None
