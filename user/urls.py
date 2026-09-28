from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import (
    UniversityView,
    CollegeView,
    DepartmentView,
    RegisterView,
    LoginView,
    ProfileView,
)

urlpatterns = [
    path("universities/", UniversityView.as_view(), name="universities"),
    path("colleges/", CollegeView.as_view(), name="colleges"),
    path("departments/", DepartmentView.as_view(), name="departments"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "universities/<int:university_id>/colleges/",
        CollegeView.as_view(),
        name="college-list",
    ),
    path(
        "universities/<int:university_id>/colleges/<int:college_id>/departments/",
        DepartmentView.as_view(),
        name="department-list",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
    ),
]
