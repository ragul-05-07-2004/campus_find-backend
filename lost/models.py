from django.db import models
from user.models import User


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.category_name


class LostItem(models.Model):
    STATUS_CHOICES = [
        ("LOST", "Lost"),
        ("FOUND", "Found"),
        ("CLAIMED", "Claimed"),
        ("CLOSED", "Closed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lost_items")

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="lost_items"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    lost_date = models.DateField()
    lost_location = models.CharField(max_length=300)

    # image = models.ImageField(upload_to="lost_items/", blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "items"

    def __str__(self):
        return self.title


class ItemDetails(models.Model):

    lost_item = models.OneToOneField(
        LostItem, on_delete=models.CASCADE, related_name="item_details"
    )

    color = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "item_details"

    def __str__(self):
        return f"Details for {self.lost_item.title}"


class ElectronicsDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="electronics"
    )

    brand = models.CharField(max_length=100, blank=True, null=True)

    model = models.CharField(max_length=100, blank=True, null=True)

    serial_number = models.CharField(max_length=200, blank=True, null=True)

    imei = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "electronics_details"


class BagDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="bag"
    )

    brand = models.CharField(max_length=100, blank=True, null=True)

    material = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "bag_details"


class BookDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="book"
    )

    subject = models.CharField(max_length=200, blank=True, null=True)

    author = models.CharField(max_length=200, blank=True, null=True)

    edition = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "book_details"


class DocumentDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="document"
    )

    document_type = models.CharField(max_length=100)

    issuing_authority = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "document_details"


class ClothingDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="clothing"
    )

    brand = models.CharField(max_length=100, blank=True, null=True)

    size = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "clothing_details"


class KeyDetails(models.Model):

    item_details = models.OneToOneField(
        ItemDetails, on_delete=models.CASCADE, related_name="key"
    )

    key_type = models.CharField(max_length=100, blank=True, null=True)

    keychain = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "key_details"


class PersonalVerificationQuestion(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_questions"
    )

    question = models.CharField(max_length=500)

    answer_hash = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "personal_verification_questions"

    def __str__(self):
        return self.question
