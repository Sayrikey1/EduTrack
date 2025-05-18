from django.urls import path
from courses.controllers.course import (
    AddLessonAPIView,
    CreateCourseAPIView,
    DeleteCourseAPIView,
    DeleteLessonAPIView,
    EnrollCourseAPIView,
    GetCourseDetailAPIView,
    ListCoursesAPIView,
    ListEnrollmentsAPIView,
    ListLessonsAPIView,
    UpdateCourseAPIView,
)

urlpatterns = [
    path("courses", ListCoursesAPIView.as_view(), name="list-courses"),
    path("courses/create", CreateCourseAPIView.as_view(), name="create-course"),
    path("courses/<int:pk>", GetCourseDetailAPIView.as_view(), name="get-course"),
    path("courses/<int:pk>/update", UpdateCourseAPIView.as_view(), name="update-course"),
    path("courses/<int:pk>/delete", DeleteCourseAPIView.as_view(), name="delete-course"),
    path("courses/<int:pk>/enroll", EnrollCourseAPIView.as_view(), name="enroll-course"),
    path("courses/enrollments", ListEnrollmentsAPIView.as_view(), name="list-enrollments"),
    path("courses/<int:pk>/lessons", ListLessonsAPIView.as_view(), name="list-lessons"),
    path("courses/<int:pk>/lessons/add", AddLessonAPIView.as_view(), name="add-lesson"),
    path("courses/<int:pk>/lessons/<int:lesson_pk>/delete", DeleteLessonAPIView.as_view(), name="delete-lesson"),
]