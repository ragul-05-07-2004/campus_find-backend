from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.hashers import make_password

from rest_framework.test import APITestCase
from rest_framework import status

from lost.models import PersonalVerificationQuestion
from user.models import University, College, Department
from user.models import User

User = get_user_model()


class PersonalVerificationQuestionAPITestCase(APITestCase):

    def setUp(self):
        # Create University
        self.university = University.objects.create(university_name="Test University")

        # Create College
        self.college = College.objects.create(
            college_name="Test College",
            college_id_number="TEST001",
            university=self.university,
        )

        # Create Department
        self.department = Department.objects.create(
            department_name="Computer Science", college=self.college
        )

        # Create User
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123",
            college=self.college,
            department=self.department,
            student_id_number="STUDENT001",
        )

        # Authenticate user
        self.client.force_authenticate(user=self.user)
        self.questions_url = reverse("personal-verification-questions")
        self.verify_url = reverse("personal-verification-verify")

    # --------------------------------
    # GET QUESTIONS
    # --------------------------------

    def test_get_questions(self):

        PersonalVerificationQuestion.objects.create(
            user=self.user,
            question="What is your favorite color?",
            answer_hash=make_password("Blue"),
        )

        response = self.client.get(self.questions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["question"], "What is your favorite color?")

    # --------------------------------
    # VERIFY CORRECT ANSWERS
    # --------------------------------

    def test_verify_correct_answer(self):

        questions = []

        for i in range(5):
            questions.append(
                PersonalVerificationQuestion.objects.create(
                    user=self.user,
                    question=f"Question {i + 1}?",
                    answer_hash=make_password(f"Answer{i + 1}"),
                )
            )

        data = {
            "answers": [
                {"question_id": questions[0].id, "answer": "Answer1"},
                {"question_id": questions[1].id, "answer": "Answer2"},
                {"question_id": questions[2].id, "answer": "Answer3"},
                {"question_id": questions[3].id, "answer": "Answer4"},
                {"question_id": questions[4].id, "answer": "Answer5"},
            ]
        }

        response = self.client.post(self.verify_url, data, format="json")

        self.assertTrue(response.data["verified"])

    def test_verify_wrong_answer(self):

        questions = []

        for i in range(5):
            questions.append(
                PersonalVerificationQuestion.objects.create(
                    user=self.user,
                    question=f"Question {i + 1}?",
                    answer_hash=make_password(f"Answer{i + 1}"),
                )
            )

        data = {
            "answers": [
                {"question_id": questions[0].id, "answer": "WrongAnswer"},
                {"question_id": questions[1].id, "answer": "Answer2"},
                {"question_id": questions[2].id, "answer": "Answer3"},
                {"question_id": questions[3].id, "answer": "Answer4"},
                {"question_id": questions[4].id, "answer": "Answer5"},
            ]
        }

        response = self.client.post(self.verify_url, data, format="json")

        self.assertFalse(response.data["verified"])
        self.assertEqual(response.data["correct_answers"], 4)
