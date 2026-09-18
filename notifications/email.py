from django.core.mail import send_mail
from django.conf import settings


def send_match_notification(lost_item, found_item, score):
    subject = "Campus-Find: Potential Match Found"

    message = f"""
Hello {lost_item.user.first_name},

We found a potential match for your lost item.

Lost Item:
{lost_item.title}

Description:
{lost_item.description}

Potential Found Item:
{found_item.title}

Description:
{found_item.description}

Match Score:
{score * 100:.2f}%

Please log in to Campus-Find to verify whether this is your item.

This is only a potential match.
Ownership verification is required before claiming the item.

Regards,
Campus-Find Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[lost_item.user.email],
        fail_silently=False,
    )
