"""Bootstrap or update the single admin account.

Usage:
    python scripts/create_admin.py                       # interactive prompts
    python scripts/create_admin.py --username X --password Y   # non-interactive

The plaintext password is never stored anywhere - only its bcrypt hash is
written to the database. This script is the only supported way to create
the first admin; afterwards, use the UI (Profile page) to change credentials.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.admin import Admin


def create_or_update_admin(username: str, password: str) -> None:
    db = SessionLocal()
    try:
        admin = db.query(Admin).first()
        if admin is None:
            admin = Admin(username=username, password_hash=hash_password(password))
            db.add(admin)
            action = "created"
        else:
            admin.username = username
            admin.password_hash = hash_password(password)
            action = "updated"
        db.commit()
        print(f"Admin {action}: username='{username}'")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update the admin account")
    parser.add_argument("--username", help="Admin username (prompted if omitted)")
    parser.add_argument("--password", help="Admin password (prompted if omitted)")
    args = parser.parse_args()

    username = args.username or input("Admin username: ").strip()
    password = args.password or getpass.getpass("Admin password: ")

    if not username or not password:
        print("Username and password are required.", file=sys.stderr)
        sys.exit(1)

    create_or_update_admin(username, password)


if __name__ == "__main__":
    main()
