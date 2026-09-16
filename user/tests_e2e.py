from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import University, College, Department, User


class UserE2ETestCase(APITestCase):

    def setUp(self):

        # ------------------------------------------------
        # 1. Create prerequisite data for admin
        # ------------------------------------------------

        self.base_university = University.objects.create(
            university_name="E2E Base University"
        )

        self.base_college = College.objects.create(
            college_name="E2E Base College",
            college_id_number="E2E_BASE_COLLEGE",
            university=self.base_university,
        )

        self.base_department = Department.objects.create(
            department_name="E2E Base Department", college=self.base_college
        )

        # ------------------------------------------------
        # 2. Create admin user
        # ------------------------------------------------

        self.admin = User.objects.create(
            email="e2e_admin@test.com",
            first_name="E2E",
            last_name="Admin",
            password=make_password("Admin@123"),
            college=self.base_college,
            department=self.base_department,
            student_id_number="E2E_ADMIN_001",
            is_active=True,
            is_staff=True,
            is_admin=True,
        )

        # ------------------------------------------------
        # 3. Generate JWT for admin
        # ------------------------------------------------

        refresh = RefreshToken.for_user(self.admin)

        self.admin_access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")

        # ------------------------------------------------
        # URLs
        # ------------------------------------------------

        self.university_url = "/api/users/universities/"
        self.college_url = "/api/users/colleges/"
        self.department_url = "/api/users/departments/"
        self.register_url = "/api/users/register/"
        self.login_url = "/api/users/login/"
        self.refresh_url = "/api/users/token/refresh/"

    def test_complete_user_flow(self):

        # ==================================================
        # STEP 1: Create University
        # ==================================================

        university_response = self.client.post(
            self.university_url,
            {"university_name": "E2E Test University"},
            format="json",
        )

        self.assertEqual(university_response.status_code, status.HTTP_201_CREATED)

        university_id = university_response.data["id"]

        # ==================================================
        # STEP 2: Create College
        # ==================================================

        college_response = self.client.post(
            self.college_url,
            {
                "college_name": "E2E Test College",
                "college_id_number": "E2E_COLLEGE_001",
                "university": university_id,
            },
            format="json",
        )

        self.assertEqual(college_response.status_code, status.HTTP_201_CREATED)

        college_id = college_response.data["id"]

        # ==================================================
        # STEP 3: Create Department
        # ==================================================

        department_response = self.client.post(
            self.department_url,
            {"department_name": "Computer Science", "college": college_id},
            format="json",
        )

        self.assertEqual(department_response.status_code, status.HTTP_201_CREATED)

        department_id = department_response.data["id"]

        # ==================================================
        # STEP 4: Register Student
        # ==================================================

        register_response = self.client.post(
            self.register_url,
            {
                "email": "e2e_student@test.com",
                "first_name": "E2E",
                "last_name": "Student",
                "password": "Student@123",
                "university": university_id,
                "college": college_id,
                "department": department_id,
                "student_id_number": "E2E_STUDENT_001",
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # ==================================================
        # STEP 5: Login Student
        # ==================================================

        login_response = self.client.post(
            self.login_url,
            {
                "email": "e2e_student@test.com",
                "password": "Student@123",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Your current code has "access_token"
        self.assertIn("access_token", login_response.data)

        self.assertIn("refresh_token", login_response.data)

        access_token = login_response.data["access_token"]
        refresh_token = login_response.data["refresh_token"]

        # ==================================================
        # STEP 6: Verify refresh cookie
        # ==================================================

        self.assertIn("refresh_token", login_response.cookies)

        # ==================================================
        # STEP 7: Use student's access token
        # ==================================================

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        protected_response = self.client.post(
            self.university_url,
            {"university_name": "E2E Protected University"},
            format="json",
        )

        self.assertEqual(protected_response.status_code, status.HTTP_201_CREATED)

        # ==================================================
        # STEP 8: Refresh token
        # ==================================================

        refresh_response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        self.assertIn("access", refresh_response.data)
