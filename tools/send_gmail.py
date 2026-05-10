#!/usr/bin/env python3
"""Send the formatted newsletter via Gmail API. Reads .tmp/newsletter.html and sends as HTML email."""

import argparse
import base64
import json
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
BASE = Path(__file__).parent.parent


def get_credentials() -> Credentials:
    token_path = BASE / "token.json"
    creds_path = BASE / "credentials.json"

    if not creds_path.exists():
        print(
            "Error: credentials.json not found in project root.\n"
            "Follow the setup guide in workflows/newsletter_automation.md to create it.",
            file=sys.stderr,
        )
        sys.exit(1)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds


def build_message(to: str, subject: str, html_body: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def main():
    parser = argparse.ArgumentParser(description="Send newsletter via Gmail")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", help="Override subject line (optional)")
    args = parser.parse_args()

    tmp = BASE / ".tmp"
    html_path = tmp / "newsletter.html"
    content_path = tmp / "newsletter_content.json"

    if not html_path.exists():
        print("Error: .tmp/newsletter.html not found. Run format_html.py first.", file=sys.stderr)
        sys.exit(1)

    html_body = html_path.read_text(encoding="utf-8")

    subject = args.subject
    if not subject and content_path.exists():
        content = json.loads(content_path.read_text())
        subject = content.get("subject_line", "Your Newsletter")

    print("Authenticating with Gmail...", file=sys.stderr)
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = build_message(args.to, subject, html_body)
    result = service.users().messages().send(userId="me", body=message).execute()

    print(f"Email sent to {args.to} — Message ID: {result['id']}", file=sys.stderr)
    print(json.dumps({"message_id": result["id"], "to": args.to, "subject": subject}))


if __name__ == "__main__":
    main()
