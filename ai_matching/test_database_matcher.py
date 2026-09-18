from lost.models import LostItem

from .matcher import calculate_django_match_score
from notifications.email import send_match_notification


def find_database_matches(lost_item):

    found_items = (
        LostItem.objects.filter(status="FOUND")
        .exclude(user_id=lost_item.user_id)
        .select_related(
            "user",
            "category",
            "item_details",
            "item_details__electronics",
            "item_details__bag",
            "item_details__book",
            "item_details__document",
            "item_details__clothing",
            "item_details__key",
        )
    )

    matches = []

    for found_item in found_items:

        result = calculate_django_match_score(lost_item, found_item)

        if result["is_match"]:

            # Change FOUND → MATCHED
            found_item.status = "MATCHED"
            found_item.save(update_fields=["status"])

            # Send notification
            send_match_notification(lost_item, found_item, result["final_score"])

            matches.append(
                {
                    "found_item_id": found_item.id,
                    "title": found_item.title,
                    "score": result["final_score"],
                    "status": found_item.status,
                    "details": result,
                }
            )

    matches.sort(key=lambda match: match["score"], reverse=True)

    return matches
