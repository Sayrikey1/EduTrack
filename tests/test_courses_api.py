# tests/test_courses_api.py

import random
import string

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.test import override_settings

from accounts.models import User, UserTypes
from courses.models import Course, Lesson, Enrollment


def get_random_first_last_name():
    first_names = [
        "Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ian", "Jack",
        "Katherine", "Liam", "Mia", "Noah", "Olivia", "Pamela", "Quincy", "Rachel", "Sam", "Tina",
        "Uma", "Victor", "Wendy", "Xander", "Yara", "Zach", "Aaron", "Bella", "Connor", "Diana"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
        "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White",
        "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Perez", "Hall"
    ]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    random_suffix = ''.join(random.choices(string.digits, k=3))
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{random_suffix}@example.com"
    username = f"{first_name.lower()}{last_name.lower()}{random_suffix}"
    return first_name, last_name, full_name, email, username


@override_settings(DEBUG=True)
class CourseAPITest(APITestCase):
    def setUp(self):
        # Create teacher1
        _, _, full_name_t1, email_t1, username_t1 = get_random_first_last_name()
        self.teacher1 = User.objects.create_user(
            username=username_t1,
            email=email_t1,
            password='Pass1234!',
            first_name=full_name_t1.split()[0],
            last_name=full_name_t1.split()[1]
        )
        self.teacher1.user_type = UserTypes.teacher
        self.teacher1.is_active = True
        self.teacher1.registration_complete = True
        self.teacher1.save()

        # Create teacher2
        _, _, full_name_t2, email_t2, username_t2 = get_random_first_last_name()
        self.teacher2 = User.objects.create_user(
            username=username_t2,
            email=email_t2,
            password='Pass1234!',
            first_name=full_name_t2.split()[0],
            last_name=full_name_t2.split()[1]
        )
        self.teacher2.user_type = UserTypes.teacher
        self.teacher2.is_active = True
        self.teacher2.registration_complete = True
        self.teacher2.save()

        # Create student1
        _, _, full_name_s1, email_s1, username_s1 = get_random_first_last_name()
        self.student1 = User.objects.create_user(
            username=username_s1,
            email=email_s1,
            password='Pass1234!',
            first_name=full_name_s1.split()[0],
            last_name=full_name_s1.split()[1]
        )
        self.student1.user_type = UserTypes.student
        self.student1.is_active = True
        self.student1.registration_complete = True
        self.student1.save()

        # Create student2
        _, _, full_name_s2, email_s2, username_s2 = get_random_first_last_name()
        self.student2 = User.objects.create_user(
            username=username_s2,
            email=email_s2,
            password='Pass1234!',
            first_name=full_name_s2.split()[0],
            last_name=full_name_s2.split()[1]
        )
        self.student2.user_type = UserTypes.student
        self.student2.is_active = True
        self.student2.registration_complete = True
        self.student2.save()

        self.client = APIClient()

    def test_teacher_cannot_be_created_by_student_and_permissions(self):
        """
        1) Student tries to create a course → should return 400 + "Only teachers can manage courses."
        2) Teacher1 creates course successfully → 200.
        3) Teacher2 (another teacher) tries to update Teacher1's course → 400 + "Permission denied."
        4) Student retrieves course detail → 200.
        5) Teacher2 tries to delete Teacher1's course → 400 + "Permission denied."
        6) Teacher1 deletes their own course → 200.
        """
        # 1) Student tries to create → 400 + error message
        self.client.force_authenticate(user=self.student1)
        data = {'title': 'Course 1', 'description': 'Desc', 'is_published': True, 'slug': 'course-1'}
        resp = self.client.post(reverse('create-course'), data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Only teachers can manage courses.']
        )

        # 2) Teacher1 creates course successfully
        self.client.force_authenticate(user=self.teacher1)
        resp = self.client.post(reverse('create-course'), data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        course_id = resp.data['id']
        self.assertEqual(resp.data['title'], 'Course 1')

        # 3) Teacher2 tries to update Teacher1's course → 400 + "Permission denied."
        self.client.force_authenticate(user=self.teacher2)
        update_data = {'title': 'Attempted Change'}
        resp = self.client.patch(reverse('update-course', args=[course_id]), update_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Permission denied.']
        )

        # 4) Student retrieves course detail → 200
        self.client.force_authenticate(user=self.student1)
        resp = self.client.get(reverse('get-course', args=[course_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], course_id)

        # 5) Teacher2 tries to delete Teacher1's course → 400 + "Permission denied."
        self.client.force_authenticate(user=self.teacher2)
        resp = self.client.delete(reverse('delete-course', args=[course_id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Permission denied.']
        )

        # 6) Teacher1 deletes their own course → 200
        self.client.force_authenticate(user=self.teacher1)
        resp = self.client.delete(reverse('delete-course', args=[course_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['message'], 'Course deleted successfully.')

    def test_student_enrollment_and_enrollment_listing_errors(self):
        """
        1) Nonexistent course ID → 400 + {"error": "Course not found."}
        2) Teacher tries to enroll → 400 + {"error": "Only students can enroll."}
        3) Student enrolls successfully → 200.
        4) Student re‐enrolls (idempotent) → 200.
        5) Student lists their enrollments → 200.
        6) Teacher lists enrollments for their own course → 200.
        7) Teacher (not owner) lists enrollments for a course → returns only those where they are teacher.
        """
        # Setup one published course by teacher1
        self.client.force_authenticate(user=self.teacher1)
        course = Course.objects.create(
            title='C2', description='Desc', teacher=self.teacher1, is_published=True, slug='c2'
        )

        # 1) Invalid course ID
        self.client.force_authenticate(user=self.student1)
        resp = self.client.post(reverse('enroll-course', args=[999]))  # nonexistent
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['non_field_errors'], ['Course not found.'])

        # 2) Teacher tries to enroll → 400 + "Only students can enroll."
        self.client.force_authenticate(user=self.teacher2)
        resp = self.client.post(reverse('enroll-course', args=[course.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['non_field_errors'], ['Only students can enroll.'])

        # 3) Student enrolls successfully → 200
        self.client.force_authenticate(user=self.student1)
        resp = self.client.post(reverse('enroll-course', args=[course.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['student'], self.student1.id)
        self.assertEqual(resp.data['course'], course.id)

        # 4) Student re‐enrolls (idempotent) → still 200
        resp2 = self.client.post(reverse('enroll-course', args=[course.id]))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data['student'], self.student1.id)

        # 5) Student lists their enrollments → 200
        resp = self.client.get(reverse('list-enrollments'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['student'], self.student1.id)

        # 6) Teacher lists enrollments for their own course → 200
        self.client.force_authenticate(user=self.teacher1)
        resp = self.client.get(reverse('list-enrollments'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['course'], course.id)

        # 7) Another teacher lists enrollments → 200 but none (they don’t own any)
        self.client.force_authenticate(user=self.teacher2)
        resp = self.client.get(reverse('list-enrollments'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 0)

    def test_lesson_crud_permissions_and_errors(self):
        """
        1) Invalid course ID on list_lessons → 400 + "Course not found."
        2) Student tries to add a lesson → 400 + "Only teachers can manage courses."
        3) Teacher (not owner) tries to add lesson → 400 + "Permission denied."
        4) Teacher1 adds lesson successfully → 200.
        5) Student lists lessons → 200 and sees the lesson.
        6) Student tries to delete lesson → 400 + "Only teachers can manage courses."
        7) Teacher (not owner) tries to delete lesson → 400 + "Permission denied."
        8) Teacher1 deletes lesson → 200.
        """
        # 1) Invalid course ID on list_lessons → 400 + "Course not found."
        self.client.force_authenticate(user=self.student1)
        resp = self.client.get(reverse('list-lessons', args=[999]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(resp.data['non_field_errors'], ['Course not found.'])

        # Create a valid course owned by teacher1
        self.client.force_authenticate(user=self.teacher1)
        course = Course.objects.create(
            title='C3', description='Desc', teacher=self.teacher1, is_published=True, slug='c3'
        )

        # Prepare lesson_data including required fields
        lesson_data = {'course': course.id, 'title': 'L1', 'content': 'Content', 'order': 1}

        # 2) Student tries to add a lesson → 400 + "Only teachers can manage courses."
        self.client.force_authenticate(user=self.student1)
        resp = self.client.post(reverse('add-lesson', args=[course.id]), lesson_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Only teachers can manage courses.']
        )

        # 3) Teacher2 (not course owner) tries to add lesson → 400 + "Permission denied."
        self.client.force_authenticate(user=self.teacher2)
        resp = self.client.post(reverse('add-lesson', args=[course.id]), lesson_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Permission denied.']
        )

        # 4) Teacher1 adds lesson successfully → 200
        self.client.force_authenticate(user=self.teacher1)
        resp = self.client.post(reverse('add-lesson', args=[course.id]), lesson_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        lesson_id = resp.data['id']
        self.assertEqual(resp.data['title'], 'L1')

        # 5) Student lists lessons → 200 + one lesson
        self.client.force_authenticate(user=self.student1)
        resp = self.client.get(reverse('list-lessons', args=[course.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['id'], lesson_id)

        # 6) Student tries to delete lesson → 400 + "Only teachers can manage courses."
        self.client.force_authenticate(user=self.student1)
        resp = self.client.delete(reverse('delete-lesson', args=[course.id, lesson_id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Only teachers can manage courses.']
        )

        # 7) Teacher2 (not owner) tries to delete → 400 + "Permission denied."
        self.client.force_authenticate(user=self.teacher2)
        resp = self.client.delete(reverse('delete-lesson', args=[course.id, lesson_id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)
        self.assertEqual(
            resp.data['non_field_errors'],
            ['Permission denied.']
        )

        # 8) Teacher1 deletes lesson → 200
        self.client.force_authenticate(user=self.teacher1)
        resp = self.client.delete(reverse('delete-lesson', args=[course.id, lesson_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['message'], 'Lesson deleted successfully.')
