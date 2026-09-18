from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import generate_embedding

# ============================================================
# WEIGHTS
# ============================================================

TITLE_WEIGHT = 0.20
DESCRIPTION_WEIGHT = 0.25
CATEGORY_WEIGHT = 0.10
LOCATION_WEIGHT = 0.10
DATE_WEIGHT = 0.05
DETAILS_WEIGHT = 0.30

MATCH_THRESHOLD = 0.70


# ============================================================
# TEXT NORMALIZATION
# ============================================================


def normalize_text(value):
    if not value:
        return ""

    return " ".join(value.lower().strip().split())


# ============================================================
# EXACT MATCH
# ============================================================


def exact_similarity(value1, value2):

    value1 = normalize_text(value1)
    value2 = normalize_text(value2)

    if not value1 or not value2:
        return 0.0

    return 1.0 if value1 == value2 else 0.0


# ============================================================
# AI SEMANTIC SIMILARITY
# ============================================================


def calculate_similarity(text1, text2):

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    embedding1 = generate_embedding(text1)
    embedding2 = generate_embedding(text2)

    score = cosine_similarity([embedding1], [embedding2])[0][0]

    return float(score)


# ============================================================
# DATE SIMILARITY
# ============================================================


def calculate_date_similarity(date1, date2):

    difference = abs((date1 - date2).days)

    if difference == 0:
        return 1.0

    elif difference == 1:
        return 0.9

    elif difference == 2:
        return 0.8

    elif difference <= 7:
        return 0.6

    elif difference <= 30:
        return 0.3

    return 0.0


# ============================================================
# GET ITEM DETAILS
# ============================================================


def get_item_details(item):

    try:
        return item.item_details

    except Exception:
        return None


# ============================================================
# ELECTRONICS
# ============================================================


def calculate_electronics_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.electronics
        found = found_item.item_details.electronics

    except Exception:
        return 0.0

    brand_score = exact_similarity(lost.brand, found.brand)

    model_score = exact_similarity(lost.model, found.model)

    return brand_score * 0.40 + model_score * 0.60


# ============================================================
# BAG
# ============================================================


def calculate_bag_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.bag
        found = found_item.item_details.bag

    except Exception:
        return 0.0

    brand_score = exact_similarity(lost.brand, found.brand)

    material_score = exact_similarity(lost.material, found.material)

    return brand_score * 0.50 + material_score * 0.50


# ============================================================
# BOOK
# ============================================================


def calculate_book_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.book
        found = found_item.item_details.book

    except Exception:
        return 0.0

    subject_score = exact_similarity(lost.subject, found.subject)

    author_score = exact_similarity(lost.author, found.author)

    edition_score = exact_similarity(lost.edition, found.edition)

    return subject_score * 0.30 + author_score * 0.40 + edition_score * 0.30


# ============================================================
# DOCUMENT
# ============================================================


def calculate_document_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.document
        found = found_item.item_details.document

    except Exception:
        return 0.0

    type_score = exact_similarity(lost.document_type, found.document_type)

    authority_score = exact_similarity(lost.issuing_authority, found.issuing_authority)

    return type_score * 0.60 + authority_score * 0.40


# ============================================================
# CLOTHING
# ============================================================


def calculate_clothing_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.clothing
        found = found_item.item_details.clothing

    except Exception:
        return 0.0

    brand_score = exact_similarity(lost.brand, found.brand)

    size_score = exact_similarity(lost.size, found.size)

    return brand_score * 0.50 + size_score * 0.50


# ============================================================
# KEY
# ============================================================


def calculate_key_score(lost_item, found_item):

    try:
        lost = lost_item.item_details.key
        found = found_item.item_details.key

    except Exception:
        return 0.0

    type_score = exact_similarity(lost.key_type, found.key_type)

    keychain_score = exact_similarity(lost.keychain, found.keychain)

    return type_score * 0.40 + keychain_score * 0.60


# ============================================================
# COLOR
# ============================================================


def calculate_color_score(lost_item, found_item):

    try:
        lost_color = lost_item.item_details.color
        found_color = found_item.item_details.color

    except Exception:
        return 0.0

    return exact_similarity(lost_color, found_color)


# ============================================================
# CATEGORY-SPECIFIC DETAILS
# ============================================================


def calculate_details_score(lost_item, found_item):

    category = normalize_text(lost_item.category.category_name)

    # --------------------------------------------------------
    # Electronics
    # --------------------------------------------------------

    if category == "electronics":

        return calculate_electronics_score(lost_item, found_item)

    # --------------------------------------------------------
    # Bag
    # --------------------------------------------------------

    elif category == "bag":

        return calculate_bag_score(lost_item, found_item)

    # --------------------------------------------------------
    # Book
    # --------------------------------------------------------

    elif category == "book":

        return calculate_book_score(lost_item, found_item)

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    elif category == "document":

        return calculate_document_score(lost_item, found_item)

    # --------------------------------------------------------
    # Clothing
    # --------------------------------------------------------

    elif category == "clothing":

        return calculate_clothing_score(lost_item, found_item)

    # --------------------------------------------------------
    # Key
    # --------------------------------------------------------

    elif category == "key":

        return calculate_key_score(lost_item, found_item)

    return 0.0


# ============================================================
# DJANGO MATCH SCORE
# ============================================================


def calculate_django_match_score(lost_item, found_item):

    # ========================================================
    # TITLE
    # ========================================================

    title_score = calculate_similarity(lost_item.title, found_item.title)

    # ========================================================
    # DESCRIPTION
    # ========================================================

    description_score = calculate_similarity(
        lost_item.description, found_item.description
    )

    # ========================================================
    # CATEGORY
    # ========================================================

    category_score = exact_similarity(
        lost_item.category.category_name, found_item.category.category_name
    )

    # ========================================================
    # LOCATION
    # ========================================================

    location_score = calculate_similarity(
        lost_item.lost_location, found_item.lost_location
    )

    # ========================================================
    # DATE
    # ========================================================

    date_score = calculate_date_similarity(lost_item.lost_date, found_item.lost_date)

    # ========================================================
    # COLOR
    # ========================================================

    color_score = calculate_color_score(lost_item, found_item)

    # ========================================================
    # CATEGORY-SPECIFIC DETAILS
    # ========================================================

    details_score = calculate_details_score(lost_item, found_item)

    # ========================================================
    # FINAL SCORE
    # ========================================================

    final_score = (
        title_score * TITLE_WEIGHT
        + description_score * DESCRIPTION_WEIGHT
        + category_score * CATEGORY_WEIGHT
        + location_score * LOCATION_WEIGHT
        + date_score * DATE_WEIGHT
        + details_score * DETAILS_WEIGHT
    )

    # ========================================================
    # MATCH DECISION
    # ========================================================

    is_match = final_score >= MATCH_THRESHOLD

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "title_score": title_score,
        "description_score": description_score,
        "category_score": category_score,
        "location_score": location_score,
        "date_score": date_score,
        "color_score": color_score,
        "details_score": details_score,
        "final_score": final_score,
        "is_match": is_match,
    }


# ============================================================
# DATABASE MULTIPLE MATCHES
# ============================================================


def find_matches(lost_item, found_items):

    matches = []

    for found_item in found_items:

        result = calculate_django_match_score(lost_item, found_item)

        if result["is_match"]:

            matches.append(
                {
                    "found_item": found_item,
                    "score": result["final_score"],
                    "details": result,
                }
            )

    matches.sort(key=lambda match: match["score"], reverse=True)

    return matches


# ============================================================
# DICTIONARY-BASED MATCHING
# ============================================================


def calculate_match_score(lost_item, found_item):

    title_score = calculate_similarity(lost_item["title"], found_item["title"])

    description_score = calculate_similarity(
        lost_item["description"], found_item["description"]
    )

    category_score = exact_similarity(lost_item["category"], found_item["category"])

    location_score = calculate_similarity(lost_item["location"], found_item["location"])

    date_score = calculate_date_similarity(lost_item["date"], found_item["date"])

    final_score = (
        title_score * TITLE_WEIGHT
        + description_score * DESCRIPTION_WEIGHT
        + category_score * CATEGORY_WEIGHT
        + location_score * LOCATION_WEIGHT
        + date_score * DATE_WEIGHT
    )

    return {
        "title_score": title_score,
        "description_score": description_score,
        "category_score": category_score,
        "location_score": location_score,
        "date_score": date_score,
        "final_score": final_score,
        "is_match": (final_score >= MATCH_THRESHOLD),
    }
