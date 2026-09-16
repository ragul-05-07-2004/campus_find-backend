from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

from user.models import University, College, Department, User


class UserSecurityTestCase(APITestCase):

    def setUp(self):

        # -----------------------------------------
        # Base organization
        # -----------------------------------------

        self.university = University.objects.create(
            university_name="Security University"
        )

        self.college = College.objects.create(
            college_name="Security College",
            college_id_number="SEC_COLLEGE_001",
            university=self.university,
        )

        self.department = Department.objects.create(
            department_name="Computer Science", college=self.college
        )

        # -----------------------------------------
        # User
        # -----------------------------------------

        self.user = User.objects.create(
            email="security@test.com",
            first_name="Security",
            last_name="User",
            password=make_password("Test@123"),
            college=self.college,
            department=self.department,
            student_id_number="SEC_STUDENT_001",
            is_active=True,
        )

        # -----------------------------------------
        # URLs
        # -----------------------------------------

        self.login_url = "/api/users/login/"
        self.university_url = "/api/users/universities/"

    def test_protected_api_without_token(self):

        response = self.client.post(
            self.university_url,
            {"university_name": "Unauthorized University"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_jwt(self):

        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")

        response = self.client.post(
            self.university_url,
            {"university_name": "Invalid JWT University"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_without_jwt(self):

        response = self.client.post(
            self.login_url,
            {
                "email": "security@test.com",
                "password": "Test@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password(self):

        response = self.client.post(
            self.login_url,
            {
                "email": "security@test.com",
                "password": "WrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed(self):

        user = User.objects.get(email="security@test.com")

        self.assertNotEqual(user.password, "Test@123")

    def test_password_hash_is_valid(self):

        user = User.objects.get(email="security@test.com")

        self.assertTrue(check_password("Test@123", user.password))

    def test_password_not_returned_in_login_response(self):

        response = self.client.post(
            self.login_url,
            {
                "email": "security@test.com",
                "password": "Test@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotIn("password", response.data)

    def test_refresh_cookie_is_httponly(self):

        response = self.client.post(
            self.login_url,
            {
                "email": "security@test.com",
                "password": "Test@123",
            },
            format="json",
        )

        cookie = response.cookies["refresh_token"]

        self.assertTrue(cookie["httponly"])

    def test_sql_injection_login(self):

        response = self.client.post(
            self.login_url,
            {
                "email": "' OR '1'='1",
                "password": "' OR '1'='1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
