"""Interactive inbox triage runner.

Usage:
    python run_triage.py                # interactive — prompts for each action
    python run_triage.py --auto-approve # approve everything (demo / smoke test)
    python run_triage.py --dry-run      # classify only, never execute writes
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from src.triage_skill import ProposedAction, TriageClient, triage_inbox

load_dotenv()

LABEL_EMOJI = {
    "billing":    "💳",
    "bug_report": "🐛",
    "sales_lead": "🤝",
    "spam":       "🗑️",
}

SEP = "─" * 64


def _preview(action: ProposedAction) -> None:
    print(f"    kind      : {action.kind}")
    print(f"    rationale : {action.rationale}")
    p = action.payload
    if action.kind == "send_reply":
        print(f"    to        : {p['to']}")
        print(f"    subject   : {p['subject']}")
        preview = p["body"].replace("\n", " ")[:110]
        print(f"    body      : {preview}…")
    elif action.kind == "send_alert":
        print(f"    channel   : {p['channel']}")
        preview = p["message"].replace("\n", " ")[:110]
        print(f"    message   : {preview}…")
    elif action.kind == "create_lead":
        print(f"    name      : {p['name']}")
        print(f"    email     : {p['email']}")
        print(f"    company   : {p.get('company')}")


def interactive_approver(email: dict, action: ProposedAction) -> bool:
    print(f"\n  {SEP}")
    _preview(action)
    while True:
        ans = input("  Approve? [y/n]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False


def auto_approver(email: dict, action: ProposedAction) -> bool:
    print(f"    ✓ auto-approved: {action.kind}")
    return True


def dry_run_approver(email: dict, action: ProposedAction) -> bool:
    print(f"    ○ dry-run, skipped: {action.kind}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the inbox triage agent")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auto-approve", action="store_true",
                       help="Approve all proposed actions without prompting")
    group.add_argument("--dry-run", action="store_true",
                       help="Classify and propose but never execute any writes")
    args = parser.parse_args()

    base_url    = os.environ.get("API_BASE_URL", "http://127.0.0.1:8099")
    read_token  = os.environ.get("READ_TOKEN",  "read-token-dev")
    write_token = os.environ.get("WRITE_TOKEN", "write-token-dev")

    if args.dry_run:
        approver = dry_run_approver
        # dry-run: deliberately omit write token — spam/dry paths never need it
        client = TriageClient(base_url, read_token=read_token)
    else:
        approver = auto_approver if args.auto_approve else interactive_approver
        client = TriageClient(base_url, read_token=read_token, write_token=write_token)

    mode = "dry-run" if args.dry_run else "auto-approve" if args.auto_approve else "interactive"

    print(f"\n{'═'*64}")
    print("  Inbox Triage Agent")
    print(f"{'═'*64}")
    print(f"  API  : {base_url}")
    print(f"  Mode : {mode}")
    print(f"{'═'*64}\n")

    try:
        results = triage_inbox(client, approver)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[error] {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'═'*64}")
    print("  Results")
    print(f"{'═'*64}")
    for r in results:
        emoji = LABEL_EMOJI.get(r.label, "?")
        n = len(r.actions)
        print(f"  {emoji}  {r.email_id}  [{r.label:<12}]  {n} action(s) proposed")
    print()


if __name__ == "__main__":
    main()
