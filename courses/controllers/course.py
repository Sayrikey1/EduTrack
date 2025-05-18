
from rest_framework.views import APIView
from django.db import transaction
from courses.services.course_service import CourseService
from courses.serializers import (
    CreateCourseSerializer, GetCourseSerializer, LessonSerializer, UpdateCourseSerializer
)
from services.util import CustomApiRequestProcessorBase
import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema


logger = logging.getLogger(__name__)

class ListCoursesAPIView(APIView, CustomApiRequestProcessorBase):
    @extend_schema(
            operation_id="listCourses",
            tags=["Courses"],
            responses={200: GetCourseSerializer(many=True)},
            )
    def get(self, request):
        service = CourseService(request)
        return self.process_request(request, service.list_courses)

class CreateCourseAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = CreateCourseSerializer

    @extend_schema(tags=["Courses"])
    @transaction.atomic
    def post(self, request):
        service = CourseService(request)
        return self.process_request(request, service.create_course)

class GetCourseDetailAPIView(APIView, CustomApiRequestProcessorBase):
    @extend_schema(
            operation_id="getCourseById",
            tags=["Courses"],
            responses={200: GetCourseSerializer()},
            )
    def get(self, request, pk=None):
        service = CourseService(request)
        return self.process_request(request, lambda: service.get_course_detail(pk))

class UpdateCourseAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = UpdateCourseSerializer

    @extend_schema(tags=["Courses"])
    @transaction.atomic
    def patch(self, request, **kwargs):
        service = CourseService(request)
        return self.process_request(request, service.update_course, **kwargs)

class DeleteCourseAPIView(APIView, CustomApiRequestProcessorBase):
    
    @extend_schema(tags=["Courses"])    
    def delete(self, request, pk=None):
        service = CourseService(request)
        return self.process_request(request, lambda: service.delete_course(pk))

class EnrollCourseAPIView(APIView, CustomApiRequestProcessorBase):
    
    @extend_schema(tags=["Courses"])    
    def post(self, request, pk=None):
        service = CourseService(request)
        return self.process_request(request, lambda: service.enroll(pk))

class ListEnrollmentsAPIView(APIView, CustomApiRequestProcessorBase):
    
    @extend_schema(tags=["Courses"])    
    def get(self, request):
        service = CourseService(request)
        return self.process_request(request, service.list_enrollments)

class ListLessonsAPIView(APIView, CustomApiRequestProcessorBase):

    @extend_schema(tags=["Courses"])    
    def get(self, request, pk=None):
        service = CourseService(request)
        return self.process_request(request, lambda: service.list_lessons(pk))

class AddLessonAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = LessonSerializer

    @extend_schema(tags=["Courses"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        service = CourseService(request)
        return self.process_request(request, service.add_lesson, **kwargs)

class DeleteLessonAPIView(APIView, CustomApiRequestProcessorBase):
    
    @extend_schema(tags=["Courses"])    
    def delete(self, request, pk=None, lesson_pk=None):
        service = CourseService(request)
        return self.process_request(request, lambda: service.delete_lesson(pk, lesson_pk))
