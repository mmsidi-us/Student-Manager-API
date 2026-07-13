# app/utils/notifications.py
import time
from datetime import datetime

def log_activity(user_id: int, action: str):
    """Appends an operational log entry to activity_log.txt with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User ID {user_id}: {action}\n"
    
    with open("activity_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

def send_notification(email: str, message: str):
    """Simulates a 2-second external network delay and logs to notification_log.txt."""
    # Simulate an external SMTP email server or SMS gateway connection delay
    time.sleep(2)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Sent to {email}: {message}\n"
    
    with open("notification_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)