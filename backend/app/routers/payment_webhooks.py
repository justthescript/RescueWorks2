import json
import os

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from .. import audit, models
from ..deps import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: str = Header(default=None, alias="Stripe-Signature"),
):
    payload = await request.body()
    sig_header = stripe_signature
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    event = None

    try:
        if secret and sig_header:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=secret
            )
        else:
            event = json.loads(payload.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    metadata = data_object.get("metadata", {}) if isinstance(data_object, dict) else {}
    payment_id = metadata.get("payment_id")

    if not payment_id:
        return {"received": True, "ignored": "no payment_id metadata"}

    try:
        payment_id_int = int(payment_id)
    except Exception:
        return {"received": True, "ignored": "invalid payment_id"}

    payment = (
        db.query(models.Payment).filter(models.Payment.id == payment_id_int).first()
    )
    if not payment:
        return {"received": True, "ignored": "payment not found"}

    previous_status = payment.status

    if event_type in ("checkout.session.completed", "payment_intent.succeeded"):
        payment.status = models.PaymentStatus.completed
        payment.status_detail = f"stripe:{event_type}"
        payment.gateway_payment_id = data_object.get("id")
    elif event_type in ("payment_intent.payment_failed",):
        payment.status = models.PaymentStatus.failed
        payment.status_detail = f"stripe:{event_type}"
        payment.gateway_payment_id = data_object.get("id")

    db.commit()

    if previous_status != payment.status:
        audit.log_action(
            db=db,
            org_id=payment.org_id,
            user_id=None,
            entity_type="payment",
            entity_id=payment.id,
            action="status_changed",
            details=f"Stripe webhook {event_type} set status from {previous_status} to {payment.status}",
        )

    return {"received": True}


@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.json()
    resource = body.get("resource", {})
    custom_id = resource.get("custom_id") or resource.get("invoice_id")

    if not custom_id:
        return {"received": True, "ignored": "no custom id"}

    try:
        payment_id = int(custom_id)
    except Exception:
        return {"received": True, "ignored": "invalid custom_id"}

    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        return {"received": True, "ignored": "payment not found"}

    previous_status = payment.status
    event_type = body.get("event_type", "")

    if event_type.endswith("PAYMENT.CAPTURE.COMPLETED") or event_type.endswith(
        "CHECKOUT.ORDER.APPROVED"
    ):
        payment.status = models.PaymentStatus.completed
        payment.status_detail = f"paypal:{event_type}"
        payment.gateway_payment_id = resource.get("id")
    elif event_type.endswith("PAYMENT.CAPTURE.DENIED"):
        payment.status = models.PaymentStatus.failed
        payment.status_detail = f"paypal:{event_type}"
        payment.gateway_payment_id = resource.get("id")

    db.commit()

    if previous_status != payment.status:
        audit.log_action(
            db=db,
            org_id=payment.org_id,
            user_id=None,
            entity_type="payment",
            entity_id=payment.id,
            action="status_changed",
            details=f"PayPal webhook {event_type} set status from {previous_status} to {payment.status}",
        )

    return {"received": True}
