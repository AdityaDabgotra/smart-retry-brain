import random
import uuid
import httpx

API_URL = "http://localhost:8000/webhooks/payment-failed"

# (error_code, error_description, category_weight_bucket)
FAILURE_TEMPLATES = [
    ("BAD_REQUEST_ERROR", "Insufficient balance in the customer's account", 0.35),
    ("GATEWAY_ERROR", "Bank server is currently down or not responding", 0.25),
    ("GATEWAY_ERROR", "Network issue while connecting to the bank, please retry", 0.20),
    ("BAD_REQUEST_ERROR", "OTP entered is incorrect", 0.12),
    ("BAD_REQUEST_ERROR", "The card has expired", 0.08),
    # Ambiguous/messy — deliberately won't match clean rule patterns, forces LLM fallback
    ("BAD_REQUEST_ERROR", "Txn declined by issuer bank, code 05", 0.03),
    ("GATEWAY_ERROR", "PSP gateway responded with an unexpected error code", 0.03),
    ("BAD_REQUEST_ERROR", "3DS authentication step could not be completed", 0.02),
]

PAYMENT_METHODS = [
    ("upi", 0.55),
    ("card", 0.30),
    ("netbanking", 0.10),
    ("wallet", 0.05),
]

BANKS = ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank", "Yes Bank"]
MERCHANTS = ["merchant_alpha", "merchant_beta", "merchant_gamma"]


def weighted_choice(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]


def generate_transaction():
    error_code, error_description, _ = random.choices(
        FAILURE_TEMPLATES, weights=[w for *_, w in FAILURE_TEMPLATES], k=1
    )[0]
    method = weighted_choice(PAYMENT_METHODS)

    return {
        "external_txn_id": f"pay_{uuid.uuid4().hex[:14]}",
        "merchant_id": random.choice(MERCHANTS),
        "amount": round(random.uniform(150, 45000), 2),
        "currency": "INR",
        "payment_method": method,
        "bank": random.choice(BANKS) if method in ("card", "netbanking") else None,
        "error_code": error_code,
        "error_description": error_description,
    }


def main(n: int = 500):
    ok, failed = 0, 0
    with httpx.Client(timeout=10.0) as client:
        for i in range(n):
            payload = generate_transaction()
            resp = client.post(API_URL, json=payload)
            if resp.status_code == 201:
                ok += 1
            else:
                failed += 1
                print(f"[{i}] {resp.status_code}: {resp.text}")
            if (i + 1) % 50 == 0:
                print(f"...{i + 1}/{n} sent")
    print(f"Done. Ingested: {ok}, failed: {failed}")


if __name__ == "__main__":
    main(500)