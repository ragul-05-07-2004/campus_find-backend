from rest_framework import serializers
from django.contrib.auth.hashers import make_password


from .models import (
    Category,
    PersonalVerificationQuestion,
    LostItem,
    ItemDetails,
    ElectronicsDetails,
    BagDetails,
    BookDetails,
    DocumentDetails,
    ClothingDetails,
    KeyDetails,
)


class CategorySerializer(serializers.ModelSerializer):

    # Dynamic fields based on category
    category_fields = serializers.SerializerMethodField(
        method_name="get_category_fields"
    )

    class Meta:
        model = Category

        fields = [
            "id",
            "category_name",
            "created_at",
            "category_fields",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "category_fields",
        ]

    def get_category_fields(self, obj):

        category = obj.category_name.lower()

        fields = {
            "electronics": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "brand",
                    "label": "Brand",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "serial_number",
                    "label": "Serial Number",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "imei",
                    "label": "IMEI",
                    "type": "text",
                    "required": False,
                },
            ],
            "clothing": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "brand",
                    "label": "Brand",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "size",
                    "label": "Size",
                    "type": "text",
                    "required": False,
                },
            ],
            "documents": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "document_type",
                    "label": "Document Type",
                    "type": "text",
                    "required": True,
                },
                {
                    "name": "issuing_authority",
                    "label": "Issuing Authority",
                    "type": "text",
                    "required": False,
                },
            ],
            "keys": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "key_type",
                    "label": "Key Type",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "keychain",
                    "label": "Keychain",
                    "type": "text",
                    "required": False,
                },
            ],
            "bags": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "brand",
                    "label": "Brand",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "material",
                    "label": "Material",
                    "type": "text",
                    "required": False,
                },
            ],
            "books": [
                {
                    "name": "color",
                    "label": "Color",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "subject",
                    "label": "Subject",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "author",
                    "label": "Author",
                    "type": "text",
                    "required": False,
                },
                {
                    "name": "edition",
                    "label": "Edition",
                    "type": "text",
                    "required": False,
                },
            ],
        }

        return fields.get(category, [])


class LostItemSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        slug_field="category_name", queryset=Category.objects.all()
    )

    details = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = LostItem

        fields = [
            "id",
            "category",
            "title",
            "description",
            "lost_date",
            "lost_location",
            "status",
            "report_type",
            "details",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "report_type",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        details_data = validated_data.pop("details", {})

        lost_item = LostItem.objects.create(**validated_data)

        item_details = ItemDetails.objects.create(
            lost_item=lost_item,
            color=details_data.get("color"),
        )

        category = lost_item.category.category_name.lower()

        if category == "electronics":

            ElectronicsDetails.objects.create(
                item_details=item_details,
                brand=details_data.get("brand"),
                model=details_data.get("model"),
                serial_number=details_data.get("serial_number"),
                imei=details_data.get("imei"),
            )

        elif category == "bags":

            BagDetails.objects.create(
                item_details=item_details,
                brand=details_data.get("brand"),
                material=details_data.get("material"),
            )

        elif category == "books":

            BookDetails.objects.create(
                item_details=item_details,
                subject=details_data.get("subject"),
                author=details_data.get("author"),
                edition=details_data.get("edition"),
            )

        elif category == "documents":

            DocumentDetails.objects.create(
                item_details=item_details,
                document_type=details_data.get("document_type"),
                issuing_authority=details_data.get("issuing_authority"),
            )

        elif category == "cloths":

            ClothingDetails.objects.create(
                item_details=item_details,
                brand=details_data.get("brand"),
                size=details_data.get("size"),
            )

        elif category == "key":

            KeyDetails.objects.create(
                item_details=item_details,
                key_type=details_data.get("key_type"),
                keychain=details_data.get("keychain"),
            )

        return lost_item


class PersonalVerificationQuestionSerializer(serializers.ModelSerializer):
    answer = serializers.CharField(
        write_only=True,
        max_length=500,
    )

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


class PersonalVerificationQuestionBulkSerializer(serializers.Serializer):
    questions = PersonalVerificationQuestionSerializer(many=True)

    def validate_questions(self, value):

        # Require exactly 5 questions
        if len(value) != 5:
            raise serializers.ValidationError(
                "Exactly 5 verification questions are required."
            )

        return value

    def create(self, validated_data):

        user = self.context["user"]

        questions_data = validated_data["questions"]

        questions = []

        for question_data in questions_data:

            answer = question_data.pop("answer")

            question_data["answer_hash"] = make_password(answer)

            questions.append(PersonalVerificationQuestion(user=user, **question_data))

        return PersonalVerificationQuestion.objects.bulk_create(questions)
