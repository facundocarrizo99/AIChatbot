import logging
import shelve
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Thread management constants
MAX_MESSAGES_PER_THREAD = 30
THREAD_TIMEOUT_MINUTES = 20
THREAD_DB_PATH = "threads_db"  # Will be created in the current directory
client = OpenAI(api_key=OPENAI_API_KEY)


class ThreadController:
    def __init__(self):
        self.threads_db = {}
        self._load_threads()

    def _load_threads(self):
        """Load existing threads from the shelf file and clear them on startup"""
        if not os.path.exists(THREAD_DB_PATH):
            os.makedirs(THREAD_DB_PATH, exist_ok=True)

        with shelve.open(os.path.join(THREAD_DB_PATH, "threads")) as db:
            self.threads_db = dict(db)
            
        # Clear all threads on startup
        self.clear_all_threads()
        
    def clear_all_threads(self):
        """Clear all threads and their data"""
        thread_count = len(self.threads_db)
        self.threads_db = {}
        self._save_threads()
        logging.info(f"Cleared {thread_count} thread(s) on startup")

    def _save_threads(self):
        """Save threads to the shelf file"""
        with shelve.open(os.path.join(THREAD_DB_PATH, "threads")) as db:
            db.update(self.threads_db)

    def get_or_create_thread(self, wa_id: str, name: str) -> Tuple[str, bool]:
        """
        Get an existing thread or create a new one if needed.
        Returns (thread_id, is_new_thread)
        """
        current_time = time.time()

        # Check if we have an existing thread that hasn't timed out
        if wa_id in self.threads_db:
            thread_data = self.threads_db[wa_id]
            last_activity = thread_data.get('last_activity', 0)
            message_count = thread_data.get('message_count', 0)

            # Check if thread is still valid
            if (current_time - last_activity < THREAD_TIMEOUT_MINUTES * 60 and
                    message_count < MAX_MESSAGES_PER_THREAD):
                # Update last activity and save
                thread_data['last_activity'] = current_time
                thread_data['message_count'] += 1
                self.threads_db[wa_id] = thread_data
                self._save_threads()
                return thread_data['thread_id'], False

        # If we get here, we need a new thread
        thread = client.beta.threads.create()
        self.threads_db[wa_id] = {
            'thread_id': thread.id,
            'last_activity': current_time,
            'message_count': 1,
            'created_at': current_time,
            'name': name
        }
        self._save_threads()
        return thread.id, True

    def cleanup_old_threads(self):
        """Remove threads that have been inactive for too long"""
        current_time = time.time()
        removed = False

        for wa_id in list(self.threads_db.keys()):
            thread_data = self.threads_db[wa_id]
            last_activity = thread_data.get('last_activity', 0)

            if current_time - last_activity >= THREAD_TIMEOUT_MINUTES * 60:
                del self.threads_db[wa_id]
                removed = True

        if removed:
            self._save_threads()


# Initialize thread manager
thread_manager = ThreadController()


def cleanup_old_threads_periodically(interval_minutes=5):
    """Run thread cleanup at regular intervals"""
    import threading

    def cleanup():
        while True:
            thread_manager.cleanup_old_threads()
            time.sleep(interval_minutes * 60)

    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup, daemon=True)
    cleanup_thread.start()


# Start the cleanup thread when the module is imported
cleanup_old_threads_periodically()