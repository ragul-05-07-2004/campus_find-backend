from rest_framework import serializers
from .models import University, College, Department, User
from django.contrib.auth.hashers import make_password, check_password


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "university_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ["id", "college_name", "college_id_number", "university", "created_at"]
        read_only_fields = ["id", "created_at"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department_name", "college", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserRegisterSerializer(serializers.ModelSerializer):

    university = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(), write_only=True
    )

    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all())

    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = User

        fields = [
            "id",
            "university",
            "college",
            "department",
            "student_id_number",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

        read_only_fields = ["id"]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
            }
        }

    def validate(self, data):

        university = data["university"]
        college = data["college"]
        department = data["department"]

        # Check college belongs to university
        if college.university_id != university.id:
            raise serializers.ValidationError(
                {"college": "This college does not belong to the selected university."}
            )

        # Check department belongs to college
        if department.college_id != college.id:
            raise serializers.ValidationError(
                {
                    "department": "This department does not belong to the selected college."
                }
            )

        return data

    def create(self, validated_data):

        # University is only used for validation.
        validated_data.pop("university")

        password = validated_data.pop("password")

        user = User(**validated_data)

        # IMPORTANT: only works if User has proper password hashing method.
        user = User(**validated_data, password=make_password(password))

        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data["email"]
        password = data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Your account is inactive."})

        if not check_password(password, user.password):
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        data["user"] = user
        return data
