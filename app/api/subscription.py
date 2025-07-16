from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..schemas.subscription import SubscriptionResponse, StripeCheckoutRequest, SubscriptionCreate
from ..models.subscription import Subscription
from ..models.user import User, SubscriptionTier, SubscriptionStatus
from ..services.stripe_service import StripeService
from ..middleware.auth_middleware import AuthMiddleware, security
import stripe
from ..config import settings

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/", response_model=SubscriptionResponse)
async def get_subscription(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's current subscription"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).order_by(Subscription.created_at.desc()).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    return subscription

@router.post("/create-checkout-session")
async def create_checkout_session(
    checkout_data: StripeCheckoutRequest,
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    stripe_service = StripeService()
    session = stripe_service.create_checkout_session(
        user.id,
        checkout_data.tier,
        checkout_data.success_url,
        checkout_data.cancel_url
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )
    
    return {"checkout_url": session.url}

@router.post("/cancel")
async def cancel_subscription(
    credentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    auth_middleware = AuthMiddleware(None, credentials)
    user = auth_middleware.get_current_user()
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Cancel with Stripe
    stripe_service = StripeService()
    if subscription.stripe_subscription_id:
        stripe_service.cancel_subscription(subscription.stripe_subscription_id)
    
    # Update local subscription
    subscription.status = SubscriptionStatus.CANCELLED
    user.subscription_status = SubscriptionStatus.CANCELLED
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session, db)
    
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_successful_payment_renewal(invoice, db)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription, db)
    
    return {"status": "success"}

async def handle_successful_payment(session, db: Session):
    """Handle successful payment from Stripe"""
    user_id = int(session['metadata']['user_id'])
    tier = SubscriptionTier(session['metadata']['tier'])
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Create or update subscription
    subscription = Subscription(
        user_id=user_id,
        stripe_subscription_id=session['subscription'],
        status=SubscriptionStatus.ACTIVE,
        tier=tier,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow()  # Will be updated by Stripe
    )
    
    db.add(subscription)
    
    # Update user
    user.subscription_tier = tier
    user.subscription_status = SubscriptionStatus.ACTIVE
    
    db.commit()

async def handle_successful_payment_renewal(invoice, db: Session):
    """Handle successful payment renewal"""
    subscription_id = invoice['subscription']
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.user.subscription_status = SubscriptionStatus.ACTIVE
        db.commit()

async def handle_subscription_cancelled(stripe_subscription, db: Session):
    """Handle subscription cancellation"""
    subscription_id = stripe_subscription['id']
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.user.subscription_status = SubscriptionStatus.CANCELLED
        subscription.user.subscription_tier = SubscriptionTier.BASIC
        db.commit()
