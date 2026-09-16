from django.urls import path
from .views import (
    CategoryListCreateView,
    LostItemCreateView,
    FoundItemCreateView,
    PersonalVerificationQuestionCreateView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("items/", LostItemCreateView.as_view(), name="lost-item-create"),
    path("verification-questions/", PersonalVerificationQuestionCreateView.as_view()),
    path("items/found/", FoundItemCreateView.as_view(), name="found-item-create"),
]
