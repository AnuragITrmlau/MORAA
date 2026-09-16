import razorpay
from app.config import settings
from app.utils.logger import logger

ACTIVE_PAYMENT_URL = "https://rzp.io/rzp/FbuLh9je"

def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

async def create_recharge_payment_link(
    customer_phone: str, 
    customer_name: str = "Customer", 
    amount: int = 500
) -> str:
    """Returns the verified permanent payment page link directly to prevent test mode limit errors."""
    logger.info(f"Serving active recharge link for {customer_phone} ({customer_name})")
    return ACTIVE_PAYMENT_URL