"""
PayPal helper stubs.

Use the PayPal REST SDK or direct HTTP calls and plug them in here.
"""


def create_order(amount: str, currency: str = "USD") -> dict:
    # TODO: call real PayPal create order
    return {
        "id": "TEST_ORDER_ID",
        "status": "CREATED",
        "amount": amount,
        "currency": currency,
    }
