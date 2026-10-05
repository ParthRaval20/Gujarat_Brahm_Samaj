"""
Development Auto-Reload Runner.
Watches for code modifications in Python files (.py) and automatically
restarts the desktop application so changes appear immediately without
having to manually close and reopen the app.
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable


class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback
        self.last_reload = 0.0

    def on_any_event(self, event):
        # Ignore directory events, temporary files, and __pycache__
        if event.is_directory:
            return
        path = event.src_path
        if not path.endswith('.py'):
            return
        if '__pycache__' in path or '.git' in path or '.pytest_cache' in path:
            return

        now = time.time()
        # Debounce multiple rapid events (save triggers multiple write events)
        if now - self.last_reload < 1.0:
            return

        self.last_reload = now
        print(f"\n[Auto-Reload] Detected change in: {os.path.basename(path)}")
        self.restart_callback()


class AppSupervisor:
    def __init__(self):
        self.process: subprocess.Popen | None = None
        self._is_restarting = False

    def start_app(self):
        main_script = os.path.join(PROJECT_ROOT, "main.py")
        print("[Auto-Reload] Starting application...")
        self.process = subprocess.Popen([PYTHON_EXE, main_script], cwd=PROJECT_ROOT)

    def restart_app(self):
        if self._is_restarting:
            return
        self._is_restarting = True
        try:
            print("[Auto-Reload] Reloading application with new changes...")
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            self.start_app()
        finally:
            self._is_restarting = False

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()


def main():
    supervisor = AppSupervisor()
    supervisor.start_app()

    event_handler = CodeChangeHandler(restart_callback=supervisor.restart_app)
    observer = Observer()
    
    # Watch code directories
    for folder in [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "ui"), os.path.join(PROJECT_ROOT, "app"),
                   os.path.join(PROJECT_ROOT, "services"), os.path.join(PROJECT_ROOT, "database")]:
        if os.path.exists(folder):
            observer.schedule(event_handler, folder, recursive=False)

    observer.start()
    print("[Auto-Reload] Monitoring for code changes... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[Auto-Reload] Stopping supervisor...")
        observer.stop()
        supervisor.stop()
    observer.join()


if __name__ == '__main__':
    main()
