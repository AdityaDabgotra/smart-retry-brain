import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification.rules import match_rule
from app.models.enums import FailureCategory


def test_insufficient_funds_matches():
    assert match_rule("Insufficient balance in the customer's account") == FailureCategory.INSUFFICIENT_FUNDS


def test_bank_timeout_matches():
    assert match_rule("Bank server is currently down or not responding") == FailureCategory.BANK_TIMEOUT


def test_network_error_matches():
    assert match_rule("Network issue while connecting to the bank, please retry") == FailureCategory.NETWORK_ERROR


def test_otp_mismatch_matches():
    assert match_rule("OTP entered is incorrect") == FailureCategory.OTP_MISMATCH


def test_card_expired_matches():
    assert match_rule("The card has expired") == FailureCategory.CARD_EXPIRED


def test_unmatched_returns_none():
    # Ambiguous descriptions should fall through to the LLM, not get force-matched
    assert match_rule("PSP gateway responded with an unexpected error code") is None