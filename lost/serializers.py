from rest_framework import serializers
from .models import Category, LostItem, Category, PersonalVerificationQuestion
from django.contrib.auth.hashers import make_password


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "category_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class LostItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = LostItem
        fields = [
            "id",
            "category",
            "title",
            "description",
            "lost_date",
            "lost_location",
            # "image",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class PersonalVerificationQuestionSerializer(serializers.ModelSerializer):

    answer = serializers.CharField(write_only=True, max_length=500)

    class Meta:
        model = PersonalVerificationQuestion
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        answer = validated_data.pop("answer")

        validated_data["answer_hash"] = make_password(answer)

        return PersonalVerificationQuestion.objects.create(**validated_data)
