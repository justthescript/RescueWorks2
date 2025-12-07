"""
Notification services - email, sms, and push.

These are stubs so you can wire in real providers like:
- Email: SendGrid, Postmark, SES
- SMS: Twilio, MessageBird
- Push: FCM or platform specific services
"""

from typing import List, Optional


def send_email(to: List[str], subject: str, body: str) -> None:
    # TODO: implement real email provider integration
    print(f"[EMAIL] to={to} subject={subject}")


def send_sms(to_number: str, body: str) -> None:
    # TODO: implement real sms provider integration
    print(f"[SMS] to={to_number} body={body}")


def send_push(
    device_token: str, title: str, body: str, data: Optional[dict] = None
) -> None:
    # TODO: implement real push notification integration
    print(f"[PUSH] token={device_token} title={title}")
