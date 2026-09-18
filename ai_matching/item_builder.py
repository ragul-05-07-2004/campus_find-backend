def build_item_text(item):
    """
    Convert a LostItem Django object into AI-readable text.
    """

    parts = []

    # -------------------------
    # Basic item information
    # -------------------------

    if item.title:
        parts.append(f"Title: {item.title}")

    if item.description:
        parts.append(f"Description: {item.description}")

    if item.category:
        parts.append(f"Category: {item.category.category_name}")

    if item.lost_location:
        parts.append(f"Location: {item.lost_location}")

    # -------------------------
    # Item details
    # -------------------------

    try:
        details = item.item_details

        if details.color:
            parts.append(f"Color: {details.color}")

        # -------------------------
        # Electronics
        # -------------------------

        try:
            electronics = details.electronics

            if electronics.brand:
                parts.append(f"Brand: {electronics.brand}")

            if electronics.model:
                parts.append(f"Model: {electronics.model}")

        except Exception:
            pass

        # -------------------------
        # Bag
        # -------------------------

        try:
            bag = details.bag

            if bag.brand:
                parts.append(f"Brand: {bag.brand}")

            if bag.material:
                parts.append(f"Material: {bag.material}")

        except Exception:
            pass

        # -------------------------
        # Book
        # -------------------------

        try:
            book = details.book

            if book.subject:
                parts.append(f"Subject: {book.subject}")

            if book.author:
                parts.append(f"Author: {book.author}")

            if book.edition:
                parts.append(f"Edition: {book.edition}")

        except Exception:
            pass

        # -------------------------
        # Document
        # -------------------------

        try:
            document = details.document

            if document.document_type:
                parts.append(f"Document Type: {document.document_type}")

            if document.issuing_authority:
                parts.append(f"Issuing Authority: {document.issuing_authority}")

        except Exception:
            pass

        # -------------------------
        # Clothing
        # -------------------------

        try:
            clothing = details.clothing

            if clothing.brand:
                parts.append(f"Brand: {clothing.brand}")

            if clothing.size:
                parts.append(f"Size: {clothing.size}")

        except Exception:
            pass

        # -------------------------
        # Key
        # -------------------------

        try:
            key = details.key

            if key.key_type:
                parts.append(f"Key Type: {key.key_type}")

            if key.keychain:
                parts.append(f"Keychain: {key.keychain}")

        except Exception:
            pass

    except Exception:
        pass

    return ". ".join(parts)
