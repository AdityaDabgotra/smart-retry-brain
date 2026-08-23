import uuid

from app.classification.rules import match_rule
from app.db.session import SessionLocal
from app.decision.service import make_decision
from app.explanation.service import generate_explanation
from app.llm.factory import get_llm_provider
from app.models.classification import FailureClassification
from app.models.enums import ClassifiedBy, FailureCategory, TransactionStatus
from app.models.transaction import Transaction


async def run_classification(error_code: str, error_description: str) -> FailureClassification:
    rule_match = match_rule(error_description)
    if rule_match is not None:
        return FailureClassification(
            id=uuid.uuid4(),
            category=rule_match,
            confidence=1.0,
            reasoning=f"Matched known error pattern for '{error_description}'",
            classified_by=ClassifiedBy.RULE_ENGINE,
        )

    llm = get_llm_provider()
    result = await llm.classify_failure(error_code, error_description)
    try:
        category = FailureCategory(result.get("category", "").lower())
    except ValueError:
        category = FailureCategory.UNKNOWN

    return FailureClassification(
        id=uuid.uuid4(),
        category=category,
        confidence=float(result.get("confidence", 0.0)),
        reasoning=result.get("reasoning", "LLM classification"),
        classified_by=ClassifiedBy.LLM,
    )


async def classify_transaction(transaction_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        txn = db.get(Transaction, transaction_id)
        if txn is None:
            return

        classification = await run_classification(txn.error_code, txn.error_description)
        classification.transaction_id = txn.id
        db.add(classification)
        db.flush()

        txn.status = TransactionStatus.CLASSIFIED
        decision = make_decision(db, txn, classification)
        db.flush()

        decision.explanation = await generate_explanation(
            txn.error_description, classification.category, decision.action
        )

        db.commit()
    finally:
        db.close()