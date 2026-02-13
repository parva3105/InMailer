#!/usr/bin/env python3
"""
Local smoke tests for backend setup.
"""

import sys
import requests
import threading
import time
from pathlib import Path

# Ensure Unicode output does not crash on Windows terminals using cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add Backend/ to import path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports() -> bool:
    print("[TEST] imports")
    try:
        from app_db import app  # noqa: F401
        from db.config import init_db  # noqa: F401
        from db.models import User, Template, EmailLog  # noqa: F401
        from mail_merge import parse_template, render_templates  # noqa: F401
        print("[OK] imports")
        return True
    except Exception as exc:
        print(f"[FAIL] imports: {exc}")
        return False


def test_database() -> bool:
    print("[TEST] database init")
    try:
        from db.config import init_db
        init_db()
        print("[OK] database init")
        return True
    except Exception as exc:
        print(f"[FAIL] database init: {exc}")
        return False


def test_server_health() -> bool:
    print("[TEST] server health")
    try:
        from app_db import app

        def run_server():
            app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(3)

        response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("[OK] server health")
            return True
        print(f"[FAIL] server health: status {response.status_code}")
        return False
    except Exception as exc:
        print(f"[FAIL] server health: {exc}")
        return False


def main():
    print("InMailer Local Backend Smoke Tests")
    print("=" * 40)

    checks = [
        ("imports", test_imports),
        ("database", test_database),
        ("health", test_server_health),
    ]

    passed = True
    for _, fn in checks:
        if not fn():
            passed = False

    print("=" * 40)
    if passed:
        print("All checks passed.")
        return 0

    print("One or more checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
