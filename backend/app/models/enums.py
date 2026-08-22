import enum

class PaymentMethod(str,enum.Enum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class TransactionStatus(str,enum.Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    SCHEDULED = "scheduled"
    RETRYING = "retrying"
    RECOVERED = "recovered"
    FAILED_PERMANENTLY = "failed_permanently"
    NEEDS_USER_ACTION = "needs_user_action"


class FailureCategory(str, enum.Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    BANK_TIMEOUT = "bank_timeout"
    OTP_MISMATCH = "otp_mismatch"
    CARD_EXPIRED = "card_expired"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class ClassifiedBy(str, enum.Enum):
    RULE_ENGINE = "rule_engine"
    LLM = "llm"


class RetryAction(str, enum.Enum):
    RETRY_IMMEDIATE = "retry_immediate"
    RETRY_SCHEDULED = "retry_scheduled"
    SWITCH_CHANNEL = "switch_channel"
    NO_RETRY = "no_retry"


class Strategy(str, enum.Enum):
    SMART = "smart"
    NAIVE = "naive"


class AttemptOutcome(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"