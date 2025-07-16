import stripe
from typing import Optional
from ..config import settings
from ..models.user import SubscriptionTier

stripe.api_key = settings.stripe_secret_key

class StripeService:
    def __init__(self):
        self.price_mapping = {
            SubscriptionTier.PRO: "price_1234567890"
        }
    
    def create_checkout_session(self, user_id: int, tier: SubscriptionTier, success_url: str, cancel_url: str):
        """Create Stripe checkout session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': self.price_mapping[tier],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'tier': tier.value
                }
            )
            return session
        except Exception as e:
            print(f"Stripe checkout error: {e}")
            return None
    
    def get_subscription(self, subscription_id: str):
        """Get subscription details from Stripe"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except Exception as e:
            print(f"Stripe subscription error: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str):
        """Cancel subscription"""
        try:
            return stripe.Subscription.delete(subscription_id)
        except Exception as e:
            print(f"Stripe cancel error: {e}")
            return None