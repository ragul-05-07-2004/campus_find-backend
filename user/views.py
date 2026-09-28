from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import University, College, Department, User
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import (
    UniversitySerializer,
    CollegeSerializer,
    DepartmentSerializer,
    UserRegisterSerializer,
    LoginSerializer,
)

# Create the university


class UniversityView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UniversitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        universities = University.objects.all().order_by("university_name")
        serializer = UniversitySerializer(universities, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Create the college


class CollegeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CollegeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, university_id):
        colleges = College.objects.filter(university_id=university_id).order_by(
            "college_name"
        )

        serializer = CollegeSerializer(colleges, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Create the department


class DepartmentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, university_id, college_id):

        departments = Department.objects.filter(
            college_id=college_id, college__university_id=university_id
        ).order_by("department_name")

        serializer = DepartmentSerializer(departments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Create the users


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {"message": "Registration successful"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            response = Response(
                {
                    "message": "Login successful",
                    "access_token": str(access),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

            # Access token
            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60 * 60,  # 1 hour
            )

            # Refresh token
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,  # 7 days
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "student_id_number": user.student_id_number,
                "college": user.college_id,
                "department": user.department_id,
            }
        )


class TokenRefreshCookieView(TokenRefreshView):

    def post(self, request, *args, **kwargs):

        # Get refresh token from the browser's HttpOnly cookie
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found in cookie"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Give the cookie value to SimpleJWT internally
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        serializer.is_valid(raise_exception=True)

        # Get newly generated access token
        access_token = serializer.validated_data["access"]

        response = Response(
            {"message": "Access token refreshed"},
            status=status.HTTP_200_OK,
        )

        # Store new access token in browser cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60,
        )

        return response
