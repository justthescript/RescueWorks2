"""
Stripe payment helpers.

Wire this up with your live Stripe keys and webhook handlers.
"""

import stripe

# You must set: stripe.api_key in your startup code


def create_checkout_session(
    amount_cents: int, currency: str, success_url: str, cancel_url: str
):
    return stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "unit_amount": amount_cents,
                    "product_data": {"name": "RescueWorks payment"},
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )
