from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class University(models.Model):
    university_name = models.CharField(max_length=400, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "universities"

    def __str__(self):
        return self.university_name


class College(models.Model):
    college_name = models.CharField(max_length=400)

    college_id_number = models.CharField(max_length=100, unique=True)

    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="colleges"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "colleges"

        constraints = [
            models.UniqueConstraint(
                fields=["university", "college_name"],
                name="unique_college_per_university",
            )
        ]

    def __str__(self):
        return self.college_name


class Department(models.Model):
    department_name = models.CharField(max_length=200)

    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name="departments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"

        constraints = [
            models.UniqueConstraint(
                fields=["college", "department_name"],
                name="unique_department_per_college",
            )
        ]

    def __str__(self):
        return self.department_name


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    college = models.ForeignKey(College, on_delete=models.PROTECT, related_name="users")

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="users"
    )

    student_id_number = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"

        constraints = [
            models.UniqueConstraint(
                fields=["college", "student_id_number"],
                name="unique_student_id_per_college",
            )
        ]

    def __str__(self):
        return self.email
