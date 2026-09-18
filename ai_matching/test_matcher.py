from datetime import date

from ai_matching.matcher import find_matches

lost_item = {
    "title": "Black Dell Laptop",
    "description": "Dell laptop with silver sticker",
    "category": "Electronics",
    "location": "CSE Department",
    "date": date(2026, 9, 15),
}


found_items = [
    {
        "id": 1,
        "title": "Dell Black Laptop",
        "description": "Black Dell laptop with silver sticker",
        "category": "Electronics",
        "location": "CSE Department",
        "date": date(2026, 9, 15),
    },
    {
        "id": 2,
        "title": "Blue Nike Shoes",
        "description": "Blue running shoes found near playground",
        "category": "Clothing",
        "location": "Playground",
        "date": date(2026, 9, 15),
    },
    {
        "id": 3,
        "title": "Dell Laptop",
        "description": "Black Dell computer found near CSE block",
        "category": "Electronics",
        "location": "CSE Department",
        "date": date(2026, 9, 16),
    },
    {
        "id": 4,
        "title": "Samsung Mobile Phone",
        "description": "Black Samsung phone with black case",
        "category": "Electronics",
        "location": "Library",
        "date": date(2026, 9, 14),
    },
    {
        "id": 5,
        "title": "Black Dell Computer",
        "description": "Dell laptop found in computer science department",
        "category": "Electronics",
        "location": "CSE Department",
        "date": date(2026, 9, 17),
    },
]


matches = find_matches(lost_item, found_items)


print("\n========== MATCH RESULTS ==========")

if not matches:

    print("No potential matches found.")

else:

    for rank, match in enumerate(matches, start=1):

        found_item = match["found_item"]

        score = match["score"]

        print("\n------------------------------")

        print("Rank:", rank)

        print("Found Item ID:", found_item["id"])

        print("Title:", found_item["title"])

        print("Match Score:", round(score * 100, 2), "%")
