from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Category, LostItem
from .serializers import (
    CategorySerializer,
    LostItemSerializer,
    PersonalVerificationQuestionSerializer,
)


class CategoryListCreateView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all().order_by("category_name")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            category = serializer.save()
            return Response(
                CategorySerializer(category).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LostItemCreateView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LostItemSerializer(data=request.data)

        if serializer.is_valid():
            lost_item = serializer.save(user=request.user)

            return Response(
                LostItemSerializer(lost_item).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonalVerificationQuestionCreateView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PersonalVerificationQuestionSerializer(data=request.data)

        if serializer.is_valid():
            question = serializer.save(user=request.user)

            return Response(
                PersonalVerificationQuestionSerializer(question).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoundItemCreateView(APIView):

    def post(self, request):
        serializer = LostItemSerializer(data=request.data)

        if serializer.is_valid():
            found_item = serializer.save(user=request.user, status="FOUND")

            return Response(
                LostItemSerializer(found_item).data, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
