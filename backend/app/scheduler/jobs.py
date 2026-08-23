from app.db.session import SessionLocal
from app.retry.executor import execute_due_retries


def run_retry_job() -> None:
    db = SessionLocal()
    try:
        count = execute_due_retries(db)
        if count:
            print(f"[scheduler] executed {count} retries")
    finally:
        db.close()