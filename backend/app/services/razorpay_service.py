import razorpay
from app.config import settings
from app.utils.logger import logger

def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

async def create_recharge_payment_link(
    customer_phone: str, 
    customer_name: str = "Customer", 
    amount: int = 500
) -> str:
    """Creates a ₹500 Razorpay standard payment link."""
    client = get_razorpay_client()
    clean_phone = customer_phone.replace("+", "").strip()

    payload = {
        "amount": amount * 100,  # Razorpay expects paise (50000 = ₹500)
        "currency": "INR",
        "accept_partial": False,
        "description": "Moraa Studio Wallet Recharge",
        "customer": {
            "name": customer_name,
            "contact": f"+{clean_phone}",
        },
        "notify": {"sms": False, "email": False},
        "reminder_enable": False,
        "notes": {
            "channel": "whatsapp",
            "sender_id": customer_phone,
        },
        "callback_method": "get"
    }

    try:
        link_res = client.payment_link.create(payload)
        short_url = link_res.get("short_url")
        logger.info(f"Created Razorpay link: {short_url} for {customer_phone}")
        return short_url
    except Exception as e:
        logger.error(f"Error generating Razorpay link: {e}")
        # Fallback dummy payment page / link
        return "https://rzp.io/l/moraa-recharge"