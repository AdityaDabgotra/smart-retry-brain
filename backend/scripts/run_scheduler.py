import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from app.scheduler.jobs import run_retry_job


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(run_retry_job, "interval", seconds=5, id="execute_due_retries")
    print("Scheduler running — polling every 5s. Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()