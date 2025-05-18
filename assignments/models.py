# apps/assignments/models.py

from django.db import models
from django.conf import settings
from courses.models import Course
from crm.models import BaseModel


class Assignment(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title}: {self.title}"


class Submission(BaseModel):
    STATUS_PENDING = "pending"
    STATUS_GRADED = "graded"
    STATUS_LATE = "late"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Review"),
        (STATUS_GRADED, "Graded"),
        (STATUS_LATE, "Late Submission"),
    ]

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    content = models.TextField()
    # file_upload = models.FileField(upload_to="submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [["assignment", "student"]]
        ordering = ["-submitted_at"]

    def save(self, *args, **kwargs):
        # Auto-update status to "late" if past due_date
        if self.submitted_at and self.assignment.due_date < self.submitted_at:
            self.status = "late"
        super().save(*args, **kwargs)
