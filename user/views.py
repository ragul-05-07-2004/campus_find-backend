from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


from .models import University, College, Department, User

from .serializers import (
    UniversitySerializer,
    CollegeSerializer,
    DepartmentSerializer,
    UserRegisterSerializer,
    LoginSerializer,
)

# Create the university


class UniversityView(APIView):

    def post(self, request):
        serializer = UniversitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create the college


class CollegeView(APIView):

    def post(self, request):
        serializer = CollegeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create the department


class DepartmentView(APIView):

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create the users


class RegisterView(APIView):

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserRegisterSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # JWT TOKEN
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            response = Response(
                {
                    "message": "Login successful",
                    "acces_token": str(access),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

            # Store REFRESH TOKEN in HttpOnly cookie
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
