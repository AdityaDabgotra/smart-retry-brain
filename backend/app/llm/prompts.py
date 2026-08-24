CLASSIFY_PROMPT = """You are a payment failure classifier. Choose exactly one category from this fixed list — do not invent new values and do not reuse the input error_code as the category:

INSUFFICIENT_FUNDS, BANK_TIMEOUT, OTP_MISMATCH, CARD_EXPIRED, NETWORK_ERROR, UNKNOWN

Examples:
error_code: GATEWAY_ERROR, description: "Bank server is currently down" -> category: BANK_TIMEOUT
error_code: BAD_REQUEST_ERROR, description: "Card has expired" -> category: CARD_EXPIRED
error_code: GATEWAY_ERROR, description: "Connection reset while contacting payment network" -> category: NETWORK_ERROR
error_code: BAD_REQUEST_ERROR, description: "Transaction declined, reason unclear" -> category: UNKNOWN
error_code: BAD_REQUEST_ERROR, description: "3DS authentication step could not be completed" -> category: OTP_MISMATCH
error_code: GATEWAY_ERROR, description: "PSP gateway responded with an unexpected error code" -> category: NETWORK_ERROR

Now classify this one:
error_code: {error_code}
description: {error_description}

Respond ONLY with valid JSON, no markdown fences, no extra text: {{"category": "ONE_OF_THE_SIX_VALUES_ABOVE", "confidence": 0.0-1.0, "reasoning": "one short sentence"}}"""


EXPLAIN_PROMPT = """You are writing a short, plain-English note for a merchant dashboard.
The customer's payment failed. Explain why in one or two friendly, non-technical sentences,
and state what happens next.

Error description: {error_description}
Failure category: {category}
Action being taken: {action}

Respond with only the explanation text, no preamble."""