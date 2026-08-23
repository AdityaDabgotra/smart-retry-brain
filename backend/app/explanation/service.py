from app.llm.factory import get_llm_provider
from app.models.enums import FailureCategory, RetryAction

ACTION_LABELS: dict[RetryAction, str] = {
    RetryAction.RETRY_IMMEDIATE: "we'll automatically retry this payment within a minute",
    RetryAction.RETRY_SCHEDULED: "we've scheduled an automatic retry",
    RetryAction.SWITCH_CHANNEL: "we'll prompt the customer to try a different payment method",
    RetryAction.NO_RETRY: "no automatic retry — this needs the customer's attention",
}


async def generate_explanation(error_description: str, category: FailureCategory, action: RetryAction) -> str:
    llm = get_llm_provider()
    action_label = ACTION_LABELS.get(action, action.value)
    return await llm.explain_decision(error_description, category.value, action_label)