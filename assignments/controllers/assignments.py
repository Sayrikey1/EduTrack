import logging
from django.db import transaction
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import OpenApiParameter, extend_schema

from assignments.services.assignment_service import AssignmentService
from assignments.serializers import (
    CreateAssignmentSerializer,
    GetAssignmentSerializer,
    UpdateAssignmentSerializer,
    SubmissionSerializer,
)
from services.util import CustomApiRequestProcessorBase

logger = logging.getLogger(__name__)


class ListAssignmentsAPIView(APIView, CustomApiRequestProcessorBase):
    """List all assignments for a given course."""
    @extend_schema(
        tags=["Course-Assignments"],
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=int,
                description="ID of the course to list assignments for",
                required=True,
            ),
        ],
        responses={200: GetAssignmentSerializer(many=True)},
    )
    def get(self, request, course_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.list_assignments(course_id)
        )


class CreateAssignmentAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = CreateAssignmentSerializer

    @extend_schema(tags=["Course-Assignments"])
    @transaction.atomic
    @method_decorator(ratelimit(key="user", rate="5/m", block=True))
    def post(self, request, course_id=None):
        service = AssignmentService(request)
        data = request.data.copy()
        data["course"] = course_id
        return self.process_request(
            request, lambda: service.create_assignment(data)
        )


class GetAssignmentDetailAPIView(APIView, CustomApiRequestProcessorBase):
    """Retrieve details of a specific assignment."""
    @extend_schema(tags=["Course-Assignments"])
    def get(self, request, assignment_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.get_assignment_detail(assignment_id)
        )


class UpdateAssignmentAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = UpdateAssignmentSerializer

    @extend_schema(tags=["Course-Assignments"])
    @transaction.atomic
    @method_decorator(ratelimit(key="user", rate="5/m", block=True))
    def patch(self, request, assignment_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.update_assignment(assignment_id, request.data)
        )


class DeleteAssignmentAPIView(APIView, CustomApiRequestProcessorBase):
    """Delete a specific assignment."""
    @extend_schema(tags=["Course-Assignments"])
    @transaction.atomic
    def delete(self, request, assignment_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.delete_assignment(assignment_id)
        )


class ListSubmissionsAPIView(APIView, CustomApiRequestProcessorBase):
    """List all submissions for an assignment (teacher only)."""
    @extend_schema(tags=["Course-Assignments"])
    def get(self, request, assignment_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.list_submissions(assignment_id)
        )


class CreateSubmissionAPIView(APIView, CustomApiRequestProcessorBase):
    serializer_class = SubmissionSerializer

    @extend_schema(tags=["Course-Assignments"])
    @transaction.atomic
    @method_decorator(ratelimit(key="user", rate="10/m", block=True))
    def post(self, request, assignment_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.create_submission(assignment_id, request.data)
        )


class GetSubmissionDetailAPIView(APIView, CustomApiRequestProcessorBase):
    @extend_schema(tags=["Course-Assignments"])
    def get(self, request, submission_id=None):
        service = AssignmentService(request)
        return self.process_request(
            request, lambda: service.get_submission_detail(submission_id)
        )


# class UpdateSubmissionAPIView(APIView, CustomApiRequestProcessorBase):
#     serializer_class = SubmissionSerializer

#     @extend_schema(tags=["Course-Assignments"])
#     @transaction.atomic
#     @method_decorator(ratelimit(key="user", rate="10/m", block=True))
#     def patch(self, request, submission_id=None):
#         service = AssignmentService(request)
#         return self.process_request(
#             request, lambda: service.update_submission(submission_id, request.data)
#         )


# class DeleteSubmissionAPIView(APIView, CustomApiRequestProcessorBase):
#     @extend_schema(tags=["Course-Assignments"])
#     @transaction.atomic
#     def delete(self, request, submission_id=None):
#         service = AssignmentService(request)
#         return self.process_request(
#             request, lambda: service.delete_submission(submission_id)
#         )
