#!/usr/bin/env python
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env file
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from rq import Queue, Worker, SimpleWorker
from app.infrastructure.queue.redis_client import get_redis_connection

if __name__ == "__main__":
    conn = get_redis_connection()
    queues = [Queue("students", connection=conn), Queue("companies", connection=conn)]
    # Use SimpleWorker for Windows (no fork)
    worker = SimpleWorker(queues, connection=conn)
    worker.work()
