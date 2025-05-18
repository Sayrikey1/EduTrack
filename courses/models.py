# apps/courses/models.py

from django.db import models
from django.conf import settings
from crm.models import BaseModel


class Course(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Lesson(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(help_text="Position within the course")
    video_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = [["course", "order"]]
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} – Lesson {self.order}: {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["student", "course"]]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
