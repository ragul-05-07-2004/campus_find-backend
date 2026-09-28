from lost.models import LostItem

from .matcher import calculate_django_match_score
from notifications.email import send_match_notification


def find_database_matches(item):
    """
    Find matching items from the database.

    LOST item  → searches FOUND items
    FOUND item → searches LOST items

    Items reported by the same user are excluded.
    """

    if item.status == "LOST":

        candidates = (
            LostItem.objects.filter(status="FOUND", report_type="FOUND")
            .exclude(user_id=item.user_id)
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

    elif item.status == "FOUND":

        candidates = (
            LostItem.objects.filter(status="LOST", report_type="LOST")
            .exclude(user_id=item.user_id)
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

    else:
        return []

    matches = []

    print("\n========== MATCHING STARTED ==========")
    print("Current item:", item.id)
    print("Title:", item.title)
    print("Status:", item.status)
    print("Candidates:", candidates.count())

    for candidate in candidates:

        print("\nComparing with:")
        print("Candidate ID:", candidate.id)
        print("Candidate title:", candidate.title)
        print("Candidate status:", candidate.status)

        result = calculate_django_match_score(item, candidate)

        score = min(max(float(result["final_score"]), 0.0), 1.0)

        print("Score:", score)
        print("Is match:", result["is_match"])

        if result["is_match"]:

            print("✅ MATCH FOUND")

            send_match_notification(item, candidate, score)

            if item.report_type == "LOST":
                lost_item_id = item.id
                found_item_id = candidate.id
            else:
                lost_item_id = candidate.id
                found_item_id = item.id

            matches.append(
                {
                    "lost_item_id": lost_item_id,
                    "found_item_id": found_item_id,
                    "title": candidate.title,
                    "status": candidate.status,
                    "score": score,
                    "details": result,
                }
            )

        else:
            print("❌ NOT A MATCH")

    matches.sort(key=lambda match: match["score"], reverse=True)

    print("\nTotal matches:", len(matches))
    print("========== MATCHING FINISHED ==========\n")

    return matches
