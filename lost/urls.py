from django.urls import path

from .views import (
    CategoryListCreateView,
    LostItemCreateView,
    FoundItemCreateView,
    PersonalVerificationQuestionCreateView,
    PersonalVerificationQuestionListView,
    CategoryListView,
    MyItemsView,
    MatchOwnershipVerifyView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("items/lost/", LostItemCreateView.as_view(), name="lost-item-create"),
    path("items/found/", FoundItemCreateView.as_view(), name="found-item-create"),
    path(
        "personal-verification-questions/create/",
        PersonalVerificationQuestionCreateView.as_view(),
        name="personal-verification-question-create",
    ),
    path(
        "personal-verification/questions/",
        PersonalVerificationQuestionListView.as_view(),
        name="personal-verification-questions",
    ),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("my-items/", MyItemsView.as_view(), name="my-items"),
    path(
        "matches/<int:match_id>/verify/",
        MatchOwnershipVerifyView.as_view(),
        name="match-ownership-verify",
    ),
]
