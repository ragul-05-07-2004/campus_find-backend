from types import SimpleNamespace

from ai_matching.item_builder import build_item_text

category = SimpleNamespace(category_name="Electronics")

electronics = SimpleNamespace(
    brand="Dell", model="Inspiron 15", serial_number="ABC123", imei=None
)

details = SimpleNamespace(color="Black", electronics=electronics)


item = SimpleNamespace(
    title="Black Dell Laptop",
    description="Dell laptop with silver sticker",
    category=category,
    lost_location="CSE Department",
    lost_date="2026-09-15",
    item_details=details,
)


text = build_item_text(item)

print("\n========== AI ITEM TEXT ==========")
print(text)
