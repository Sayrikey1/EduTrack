import logging
from typing import Any, Dict, List, Optional, Tuple

from django.core.cache import cache

from accounts.models import User, UserTypes
from courses.models import Course, Lesson, Enrollment
from courses.serializers import (
    CreateCourseSerializer,
    GetCourseSerializer,
    UpdateCourseSerializer,
    LessonSerializer,
    EnrollmentSerializer,
)
from services.cache_util import CacheUtil
from services.pagination import ServicePaginationMixin

logger = logging.getLogger(__name__)


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
        cache_key = CacheUtil.generate_cache_key("published_courses_list")
        def loader():
            qs = Course.objects.filter(is_published=True)
            data = self.paginate(qs, GetCourseSerializer, self.request)
            return data, None

        data, _ = CacheUtil.get_cache_value_or_default(
            cache_key,
            value_callback=loader,
            require_fresh_data=False,
            timeout=300,
        )
        return data or [], None

    def create_course(self, validated_data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error

        serializer = CreateCourseSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save(teacher=teacher)

        # invalidate list + detail caches
        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("published_courses_list"),
            CacheUtil.generate_cache_key("course_detail", str(course.id))
        )

        return GetCourseSerializer(course).data, None

    def get_course_detail(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        cache_key = CacheUtil.generate_cache_key("course_detail", pk)

        def loader():
            course, err = self._get_course(pk)
            if err:
                return None, err
            return GetCourseSerializer(course).data, None

        data, error = CacheUtil.get_cache_value_or_default(
            cache_key,
            value_callback=loader,
            require_fresh_data=False,
            timeout=300,
        )
        return data, error

    def update_course(
        self, validated_data: Dict[str, Any], **kwargs
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error
        
        pk = kwargs.get("pk")
        if not pk:
            return None, "Course ID not provided."
        if not validated_data:
            return None, "No data provided for update."
        course, error = self._get_course(pk)
        if error:
            return None, error
        if course.teacher != teacher:
            return None, "Permission denied."

        serializer = UpdateCourseSerializer(course, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        # invalidate caches
        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("published_courses_list"),
            CacheUtil.generate_cache_key("course_detail", pk)
        )

        return GetCourseSerializer(updated).data, None

    def delete_course(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error

        course, error = self._get_course(pk)
        if error:
            return None, error
        if course.teacher != teacher:
            return None, "Permission denied."

        course.delete()

        # invalidate caches
        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("published_courses_list"),
            CacheUtil.generate_cache_key("course_detail", pk)
        )

        return {"message": "Course deleted successfully."}, None

    # ------------------------------------
    # Enrollment methods
    # ------------------------------------
    def enroll(self, pk: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        course, error = self._get_course(pk)
        if error:
            return None, error

        student = self.auth_user
        if student.user_type != UserTypes.student:
            return None, "Only students can enroll."

        enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
        return EnrollmentSerializer(enrollment).data, None

    def list_enrollments(self) -> Tuple[List[Dict[str, Any]], None]:
        qs = (
            Enrollment.objects.filter(course__teacher=self.auth_user)
            if self.auth_user.user_type == UserTypes.teacher
            else Enrollment.objects.filter(student=self.auth_user)
        )
        data = self.paginate(qs, EnrollmentSerializer, self.request)
        return data, None

    # ------------------------------------
    # Lesson methods
    # ------------------------------------
    def list_lessons(
        self, course_pk: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        course, error = self._get_course(course_pk)
        if error:
            return [], error

        lessons_qs = course.lessons.all()
        data = self.paginate(lessons_qs, LessonSerializer, self.request)
        return data, None

    def add_lesson(
        self, validated_data: Dict[str, Any], **kwargs
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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

        validated_data["course"] = course.id
        serializer = LessonSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return LessonSerializer(lesson).data, None

    def delete_lesson(
        self, course_pk: str, lesson_pk: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
