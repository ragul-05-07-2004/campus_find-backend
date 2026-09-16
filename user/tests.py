from django.test import TestCase
from django.contrib.auth.hashers import make_password

from .models import User, University, College, Department
from .serializers import LoginSerializer


class LoginSerializerTestCase(TestCase):

    def setUp(self):

        self.university = University.objects.create(university_name="Test University")

        self.college = College.objects.create(
            college_name="Test College",
            college_id_number="COL001",
            university=self.university,
        )

        self.department = Department.objects.create(
            department_name="Computer Science", college=self.college
        )

        self.user = User.objects.create(
            email="test@gmail.com",
            first_name="Ragul",
            last_name="R",
            password=make_password("Test@123"),
            college=self.college,
            department=self.department,
            student_id_number="STU001",
            is_active=True,
        )

    def test_valid_login(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        serializer = LoginSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_password(self):

        data = {"email": "test@gmail.com", "password": "WrongPassword"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertEqual(serializer.errors["detail"][0], "Invalid email or password.")

    def test_invalid_email(self):

        data = {"email": "wrong@gmail.com", "password": "Test@123"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertEqual(serializer.errors["detail"][0], "Invalid email or password.")

    def test_inactive_user(self):

        self.user.is_active = False
        self.user.save()

        data = {"email": "test@gmail.com", "password": "Test@123"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertEqual(serializer.errors["detail"][0], "Your account is inactive.")

    def test_invalid_email_format(self):

        data = {"email": "not-an-email", "password": "Test@123"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("email", serializer.errors)

    def test_missing_email(self):

        data = {"password": "Test@123"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("email", serializer.errors)

    def test_missing_password(self):

        data = {"email": "test@gmail.com"}

        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("password", serializer.errors)

    def test_password_is_write_only(self):

        serializer = LoginSerializer()

        password_field = serializer.fields["password"]

        self.assertTrue(password_field.write_only)


from django.test import TestCase
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from .models import User, University, College, Department


class LoginViewTestCase(APITestCase):

    def setUp(self):

        # University
        self.university = University.objects.create(university_name="Test University")

        # College
        self.college = College.objects.create(
            college_name="Test College",
            college_id_number="COL001",
            university=self.university,
        )

        # Department
        self.department = Department.objects.create(
            department_name="Computer Science", college=self.college
        )

        # User
        self.user = User.objects.create(
            email="test@gmail.com",
            first_name="Ragul",
            last_name="R",
            password=make_password("Test@123"),
            college=self.college,
            department=self.department,
            student_id_number="STU001",
            is_active=True,
        )

    # 1. Valid login
    def test_valid_login(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. Check success message
    def test_login_success_message(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.data["message"], "Login successful")

    # 3. Check access token
    def test_access_token_generated(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertIn("acces_token", response.data)

        self.assertTrue(response.data["acces_token"])

    # 4. Check refresh token
    def test_refresh_token_generated(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertIn("refresh_token", response.data)

        self.assertTrue(response.data["refresh_token"])

    # 5. Check refresh token cookie
    def test_refresh_token_cookie(self):

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertIn("refresh_token", response.cookies)

        cookie = response.cookies["refresh_token"]

        self.assertTrue(cookie["httponly"])

    # 6. Wrong password
    def test_wrong_password(self):

        data = {"email": "test@gmail.com", "password": "WrongPassword"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data["detail"][0], "Invalid email or password.")

    # 7. Invalid email / user doesn't exist
    def test_invalid_email(self):

        data = {"email": "wrong@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data["detail"][0], "Invalid email or password.")

    # 8. Inactive user
    def test_inactive_user(self):

        self.user.is_active = False
        self.user.save()

        data = {"email": "test@gmail.com", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data["detail"][0], "Your account is inactive.")

    # 9. Missing email
    def test_missing_email(self):

        data = {"password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email", response.data)

    # 10. Missing password
    def test_missing_password(self):

        data = {"email": "test@gmail.com"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("password", response.data)

    # 11. Invalid email format
    def test_invalid_email_format(self):

        data = {"email": "invalid-email", "password": "Test@123"}

        response = self.client.post("/api/users/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email", response.data)

    # 12. Empty request
    def test_empty_request(self):

        response = self.client.post("/api/users/login/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 13. last_login updated
    def test_last_login_updated(self):

        self.assertIsNone(self.user.last_login)

        data = {"email": "test@gmail.com", "password": "Test@123"}

        before_login = timezone.now()

        response = self.client.post("/api/users/login/", data, format="json")

        after_login = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertIsNotNone(self.user.last_login)

        self.assertGreaterEqual(self.user.last_login, before_login)

        self.assertLessEqual(self.user.last_login, after_login)
