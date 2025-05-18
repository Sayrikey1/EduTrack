from django.urls import path
from assignments.controllers.assignments import (
    ListAssignmentsAPIView,
    CreateAssignmentAPIView,
    GetAssignmentDetailAPIView,
    UpdateAssignmentAPIView,
    DeleteAssignmentAPIView,
    ListSubmissionsAPIView,
    CreateSubmissionAPIView,
    GetSubmissionDetailAPIView
)

urlpatterns = [
    path("courses/<int:course_id>/assignments", ListAssignmentsAPIView.as_view(), name="list-assignments"),
    path("courses/<int:course_id>/assignments/create", CreateAssignmentAPIView.as_view(), name="create-assignment"),
    path("assignments/<int:assignment_id>", GetAssignmentDetailAPIView.as_view(), name="get-assignment"),
    path("assignments/<int:assignment_id>/update", UpdateAssignmentAPIView.as_view(), name="update-assignment"),
    path("assignments/<int:assignment_id>/delete", DeleteAssignmentAPIView.as_view(), name="delete-assignment"),
    path("assignments/<int:assignment_id>/submissions", ListSubmissionsAPIView.as_view(), name="list-submissions"),
    path("assignments/<int:assignment_id>/submissions/create", CreateSubmissionAPIView.as_view(), name="create-submission"),
    path("submissions/<int:submission_id>", GetSubmissionDetailAPIView.as_view(), name="get-submission"),
    # path("submissions/<int:submission_id>/update", UpdateSubmissionAPIView.as_view(), name="update-submission"),
    # path("submissions/<int:submission_id>/delete", DeleteSubmissionAPIView.as_view(), name="delete-submission"),
]
