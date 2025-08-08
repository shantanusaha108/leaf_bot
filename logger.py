# leafbot_project/logger.py
import os
import atexit
from datetime import datetime
import random

# Create a unique session ID
session_id = random.randint(1000, 9999)
start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")

# At server start
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"\n--- START SESSION {session_id} at {start_time} ---\n")

def log_error(error_type: str, description: str):
    """
    Centralized error logging.
    Writes: [time] error_type: description
    """
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{time_now}] {error_type.upper()}: {description}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

# On server stop
def end_session():
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"--- END SESSION {session_id} at {end_time} ---\n")

atexit.register(end_session)
