import logging
from typing import Any, Dict, List, Optional, Tuple

from accounts.models import User, UserTypes
from assignments.models import Assignment, Submission
from assignments.serializers import (
    CreateAssignmentSerializer,
    GetAssignmentSerializer,
    UpdateAssignmentSerializer,
    SubmissionSerializer,
)
from services.cache_util import CacheUtil
from services.log import AppLogger
from services.pagination import ServicePaginationMixin

logger = logging.getLogger(__name__)


class AssignmentService(ServicePaginationMixin):
    def __init__(self, request):
        self.request = request
        self.auth_user: User = request.user

    # -----------------------------
    # Helper Methods
    # -----------------------------
    def _get_teacher(self) -> Tuple[Optional[User], Optional[str]]:
        if not self.auth_user.is_authenticated:
            return None, "Authentication required."
        if self.auth_user.user_type != UserTypes.teacher:
            return None, "Only teachers can manage assignments."
        return self.auth_user, None

    @staticmethod
    def _get_assignment(pk: str) -> Tuple[Optional[Assignment], Optional[str]]:
        if not pk:
            return None, "Assignment ID not provided."
        try:
            return Assignment.objects.get(id=pk), None
        except Assignment.DoesNotExist:
            return None, "Assignment not found."

    # -----------------------------
    # Assignment Methods
    # -----------------------------
    def list_assignments(
        self, course_id: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        cache_key = CacheUtil.generate_cache_key("assignments_list", course_id)

        def loader():
            qs = Assignment.objects.filter(course_id=course_id)
            data = self.paginate(qs, GetAssignmentSerializer, self.request)
            return data, None

        data, error = CacheUtil.get_cache_value_or_default(
            cache_key,
            value_callback=loader,
            require_fresh_data=False,
            timeout=300,
        )
        return data or [], error

    def create_assignment(
        self, validated_data: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error

        course = validated_data.get("course")
        if course.teacher.user != teacher:
            return None, "Permission denied."

        serializer = CreateAssignmentSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()

        # invalidate caches for this course
        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("assignments_list", str(course.id))
        )

        return GetAssignmentSerializer(assignment).data, None

    def get_assignment_detail(
        self, pk: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        cache_key = CacheUtil.generate_cache_key("assignment_detail", pk)

        def loader():
            assignment, err = self._get_assignment(pk)
            if err:
                return None, err
            return GetAssignmentSerializer(assignment).data, None

        data, error = CacheUtil.get_cache_value_or_default(
            cache_key,
            value_callback=loader,
            require_fresh_data=False,
            timeout=300,
        )
        return data, error

    def update_assignment(
        self, pk: str, validated_data: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error

        assignment, error = self._get_assignment(pk)
        if error:
            return None, error
        if assignment.course.teacher.user != teacher:
            return None, "Permission denied."

        serializer = UpdateAssignmentSerializer(
            assignment, data=validated_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        # invalidate both list + detail
        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("assignments_list", str(updated.course.id)),
            CacheUtil.generate_cache_key("assignment_detail", pk),
        )

        return GetAssignmentSerializer(updated).data, None

    def delete_assignment(
        self, pk: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return None, error

        assignment, error = self._get_assignment(pk)
        if error:
            return None, error
        if assignment.course.teacher.user != teacher:
            return None, "Permission denied."

        course_id = assignment.course.id
        assignment.delete()

        CacheUtil.clear_cache(
            CacheUtil.generate_cache_key("assignments_list", str(course_id)),
            CacheUtil.generate_cache_key("assignment_detail", pk),
        )

        return {"message": "Assignment deleted"}, None

    # -----------------------------
    # Submission Methods
    # -----------------------------
    def list_submissions(
        self, assignment_id: str
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        teacher, error = self._get_teacher()
        if error:
            return [], error

        qs = Submission.objects.filter(assignment_id=assignment_id)
        data = self.paginate(qs, SubmissionSerializer, self.request)
        return data, None

    def create_submission(
        self, assignment_id: str, validated_data: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        user = self.auth_user
        assignment, error = self._get_assignment(assignment_id)
        if error:
            return None, error
        if user.user_type != UserTypes.student:
            return None, "Only students can submit."

        validated_data["assignment"] = assignment
        validated_data["student"] = user
        serializer = SubmissionSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        return SubmissionSerializer(submission).data, None

    def get_submission_detail(
        self, pk: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        submission = self._get_submission(pk)
        if not submission:
            return None, "Submission not found."
        return SubmissionSerializer(submission).data, None

    def update_submission(
        self, pk: str, validated_data: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        user = self.auth_user
        submission = self._get_submission(pk)
        if not submission:
            return None, "Submission not found."
        if submission.student != user:
            return None, "Permission denied."

        serializer = SubmissionSerializer(
            submission, data=validated_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return SubmissionSerializer(updated).data, None

    def delete_submission(
        self, pk: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        user = self.auth_user
        submission = self._get_submission(pk)
        if not submission:
            return None, "Submission not found."
        if submission.student != user:
            return None, "Permission denied."
        submission.delete()
        return {"message": "Submission deleted"}, None

    # -----------------------------
    # Internal Fetch
    # -----------------------------
    def _get_submission(self, pk: str) -> Optional[Submission]:
        if not pk:
            return None
        try:
            return Submission.objects.get(id=pk)
        except Submission.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching submission: {e}")
            return None
