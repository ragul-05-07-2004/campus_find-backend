from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ai_matching.database_matcher import find_database_matches
from django.contrib.auth.hashers import check_password
from rest_framework import status
from django.db import transaction


from .models import (
    Category,
    LostItem,
    PersonalVerificationQuestion,
    ItemMatch,
    Notification,
)

from .serializers import (
    CategorySerializer,
    LostItemSerializer,
    PersonalVerificationQuestionSerializer,
    PersonalVerificationQuestionBulkSerializer,
    PersonalVerificationQuestion,
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


class CategoryListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        categories = Category.objects.all().order_by("category_name")

        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LostItemCreateView(APIView):

    def get(self, request):

        lost_items = LostItem.objects.filter(
            user=request.user, report_type="LOST"
        ).order_by("-created_at")

        serializer = LostItemSerializer(lost_items, many=True)

        return Response(
            {"count": lost_items.count(), "items": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = LostItemSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # --------------------------------
        # 1. Create LOST item
        # --------------------------------

        lost_item = serializer.save(
            user=request.user, status="LOST", report_type="LOST"
        )

        # --------------------------------
        # 2. AI searches FOUND items
        # --------------------------------

        matches = find_database_matches(lost_item)

        print("MATCH RESULTS:", matches)

        created_matches = []

        # --------------------------------
        # 3. Save every AI match
        # --------------------------------

        for match in matches:

            try:
                found_item = LostItem.objects.get(
                    id=match["found_item_id"], report_type="FOUND", status="FOUND"
                )

            except LostItem.DoesNotExist:
                continue

            # Create ItemMatch
            item_match, created = ItemMatch.objects.get_or_create(
                lost_item=lost_item,
                found_item=found_item,
                defaults={"score": match["score"]},
            )
            if created:
                Notification.objects.create(
                    user=lost_item.user,
                    notification_type="MATCH_FOUND",
                    match=item_match,
                    message="A potential match was found for your lost item.",
                )

            # If match already exists, update score
            if not created:
                item_match.score = match["score"]
                item_match.save(update_fields=["score"])

            # --------------------------------
            # 4. Update statuses
            # --------------------------------

            lost_item.status = "MATCHED"
            found_item.status = "MATCHED"

            lost_item.save(update_fields=["status"])
            found_item.save(update_fields=["status"])

            # --------------------------------
            # 5. Add match_id to response
            # --------------------------------

            created_matches.append({**match, "match_id": item_match.id})

        # --------------------------------
        # 6. Refresh lost item
        # --------------------------------

        lost_item.refresh_from_db()

        return Response(
            {"item": LostItemSerializer(lost_item).data, "matches": created_matches},
            status=status.HTTP_201_CREATED,
        )


class FoundItemCreateView(APIView):

    def post(self, request):

        serializer = LostItemSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # --------------------------------
        # 1. Create FOUND item
        # --------------------------------

        found_item = serializer.save(
            user=request.user, status="FOUND", report_type="FOUND"
        )

        # --------------------------------
        # 2. AI searches LOST items
        # --------------------------------

        matches = find_database_matches(found_item)

        print("MATCH RESULTS:", matches)

        created_matches = []

        # --------------------------------
        # 3. Save every AI match
        # --------------------------------

        for match in matches:

            try:
                lost_item = LostItem.objects.get(
                    id=match["lost_item_id"], report_type="LOST", status="LOST"
                )

            except LostItem.DoesNotExist:
                continue

            # --------------------------------
            # 4. Create ItemMatch
            # --------------------------------

            item_match, created = ItemMatch.objects.get_or_create(
                lost_item=lost_item,
                found_item=found_item,
                defaults={"score": match["score"]},
            )
            if created:
                Notification.objects.create(
                    user=lost_item.user,
                    notification_type="MATCH_FOUND",
                    match=item_match,
                    message="A potential match was found for your lost item.",
                )

            # Update score if match already exists
            if not created:
                item_match.score = match["score"]
                item_match.save(update_fields=["score"])

            # --------------------------------
            # 5. Update statuses
            # --------------------------------

            lost_item.status = "MATCHED"
            found_item.status = "MATCHED"

            lost_item.save(update_fields=["status"])
            found_item.save(update_fields=["status"])

            # --------------------------------
            # 6. Add match_id
            # --------------------------------

            created_matches.append({**match, "match_id": item_match.id})

        # --------------------------------
        # 7. Refresh item
        # --------------------------------

        found_item.refresh_from_db()

        return Response(
            {"item": LostItemSerializer(found_item).data, "matches": created_matches},
            status=status.HTTP_201_CREATED,
        )


class MyItemsView(APIView):

    def get(self, request):

        items = LostItem.objects.filter(user=request.user).order_by("-created_at")

        serializer = LostItemSerializer(items, many=True)

        return Response(
            {"count": items.count(), "items": serializer.data},
            status=status.HTTP_200_OK,
        )


class PersonalVerificationQuestionCreateView(APIView):

    @transaction.atomic
    def post(self, request):

        serializer = PersonalVerificationQuestionBulkSerializer(
            data=request.data, context={"user": request.user}
        )

        if serializer.is_valid():
            questions = serializer.save()

            return Response(
                {
                    "message": "Verification questions created successfully.",
                    "questions": [
                        {
                            "id": question.id,
                            "question": question.question,
                            "created_at": question.created_at,
                            "updated_at": question.updated_at,
                        }
                        for question in questions
                    ],
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PersonalVerificationQuestionListView(APIView):

    def get(self, request):

        questions = PersonalVerificationQuestion.objects.filter(user=request.user)

        serializer = PersonalVerificationQuestionSerializer(questions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MatchOwnershipVerifyView(APIView):

    @transaction.atomic
    def post(self, request, match_id):

        answers = request.data.get("answers", [])

        if len(answers) != 5:
            return Response(
                {"error": "Exactly 5 answers are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get exact match
        try:
            match = (
                ItemMatch.objects.select_for_update()
                .select_related("lost_item", "found_item")
                .get(id=match_id)
            )

        except ItemMatch.DoesNotExist:
            return Response(
                {"error": "Match not found."}, status=status.HTTP_404_NOT_FOUND
            )

        lost_item = match.lost_item
        found_item = match.found_item

        # Only lost-item owner can verify
        if lost_item.user_id != request.user.id:
            return Response(
                {
                    "error": "Only the owner of the lost item can perform ownership verification."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Match must still be active
        if lost_item.status != "MATCHED" or found_item.status != "MATCHED":
            return Response(
                {"error": "This match is no longer active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get owner's verification questions
        questions = PersonalVerificationQuestion.objects.filter(user=request.user)

        if questions.count() != 5:
            return Response(
                {"error": "You must have exactly 5 verification questions."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract question IDs
        question_ids = [item.get("question_id") for item in answers]

        # Prevent duplicate questions
        if len(set(question_ids)) != 5:
            return Response(
                {"error": "Each question must be answered only once."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        correct = 0

        # Check all 5 answers
        for item in answers:

            question_id = item.get("question_id")
            answer = item.get("answer", "").strip()

            try:
                question = questions.get(id=question_id)

            except PersonalVerificationQuestion.DoesNotExist:
                continue

            if check_password(answer, question.answer_hash):
                correct += 1

        # Verification failed
        if correct != 5:

            lost_item.status = "LOST"
            found_item.status = "FOUND"

            lost_item.save(update_fields=["status"])
            found_item.save(update_fields=["status"])

            return Response(
                {
                    "verified": False,
                    "message": "Ownership verification failed.",
                    "correct_answers": correct,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verification successful
        lost_item.status = "CLAIMED"
        found_item.status = "CLAIMED"

        lost_item.save(update_fields=["status"])
        found_item.save(update_fields=["status"])

        return Response(
            {
                "verified": True,
                "message": "Ownership verified successfully.",
                "match_id": match.id,
                "lost_item_id": lost_item.id,
                "found_item_id": found_item.id,
                "lost_item_status": lost_item.status,
                "found_item_status": found_item.status,
                "match_score": match.score,
            },
            status=status.HTTP_200_OK,
        )
