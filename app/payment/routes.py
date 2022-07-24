"""Public routes"""
import logging

from app import csrf, db, stripe
from app.auth.models import User, UserSubscription
from flask import (abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from . import payment_bp

logger = logging.getLogger(__name__)

@payment_bp.route("/")
def card():    
    return render_template("payment/card.html")

@payment_bp.route("/create/session/", methods=["POST"])
@login_required
def create_session():
    if current_user.get_subscription():
        return redirect(url_for("payment.manage_suscription"))

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": "price_1LNPcmGR4goX6nqtxYoxoHW8",
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=url_for("payment.manage_suscription", _external=True),
        cancel_url=url_for("payment.manage_suscription", _external=True),
    )

    new_subscription = UserSubscription(id_user = current_user.id, token = session.id)

    new_subscription.save()

    return redirect(session.url, code=303)    

@payment_bp.route("/webhook", methods=["POST"])
@csrf.exempt
def webhook():
    try:
        if request.content_length > 1024 * 1024:
            abort(413)

        db.session.begin_nested() # db checkpoint
        
        payload = request.get_data()
        sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            
        except ValueError:
            return {}, 400

        except stripe.error.SignatureVerificationError:
            return {}, 400

        user_subscription = None
        payment_status = None
        if event["type"] == "customer.subscription.updated":
            user_subscription = UserSubscription.get_by_external_id(event["data"]["object"]["customer"])
            if event["data"]["previous_attributes"].get("canceled_at") is not None:
                payment_status = "paid"

        elif event["type"] == "checkout.session.completed":
            user_subscription = UserSubscription.get_by_token(event["data"]["object"]["id"])
            user_subscription.external_id = event["data"]["object"]["customer"]
            payment_status = event["data"]["object"]["payment_status"]

        id_user = None if not user_subscription else user_subscription.id_user
        user = User.get_by_id(id_user)

        if user and user_subscription:
            user.suscription_active = False
            if (payment_status == 'paid'):
                user.suscription_active = True

        db.session.commit()

    except Exception as e:
        logging.error(e)

    return {}


@payment_bp.route("/manage/suscription/")
@login_required
def manage_suscription():
    if not current_user.get_subscription():
        flash("Parece que no tienes una suscripción activa", "warning")
        return redirect(url_for("payment.card"))

    checkout_session = stripe.checkout.Session.retrieve(
        current_user.get_subscription().token
    )

    return_url = url_for("public.home", _external=True)

    try:
        portalSession = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=return_url,
        )

    except Exception:
        flash("Hubo un error con tu suscripción", "danger")
        UserSubscription.get_by_token(current_user.get_subscription().token).delete()
        db.session.commit()
        return redirect(url_for("payment.card"))

    return redirect(portalSession.url, code=303)
    
