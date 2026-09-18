"""CLI and entry point for AIONOS Assignment 1 — Executive Action Copilot.

Usage:
    python main.py                     # Runs full pipeline and outputs Friday 25 Sep 2026 Daily Brief
    python main.py --date 2026-09-23   # Outputs Daily Brief as of Wednesday 23 Sep 2026
    python main.py --ask "What did I promise Raghav?"
    python main.py --ask "What needs action today?"
    python main.py --interactive       # Interactive Q&A shell
"""
import sys
import argparse
from datetime import datetime, date

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from copilot import ExecutiveActionCopilot


def parse_date_arg(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, "%d %b %Y").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{date_str}'. Expected YYYY-MM-DD or DD-MM-YYYY.")


def main():
    parser = argparse.ArgumentParser(
        description="AIONOS Assignment 1 — Executive Action Copilot (Arjun Malhotra, VP Sales)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="2026-09-25",
        help="Reference date for daily brief & urgency calculation (default: 2026-09-25, Friday of data pack week)",
    )
    parser.add_argument(
        "--ask",
        type=str,
        help="Direct question to ask the Copilot (e.g., 'What did I promise Raghav?')",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive terminal mode to query the copilot",
    )
    parser.add_argument(
        "--no-evidence",
        action="store_true",
        help="Omit raw source evidence citations in the brief output",
    )

    args = parser.parse_args()
    target_date = parse_date_arg(args.date)

    copilot = ExecutiveActionCopilot(default_reference_date=target_date)
    brief = copilot.run_pipeline()

    if args.ask:
        ans = copilot.ask(args.ask)
        print("\n" + "=" * 70)
        print(f"QUERY: {args.ask}")
        print("=" * 70)
        print(ans["answer"])
        print("\n--- SOURCE EVIDENCE ---")
        for ev in ans.get("evidence", []):
            print(f"• {ev}")
        print("=" * 70 + "\n")
        return

    if args.interactive:
        print("\n" + "=" * 75)
        print(f"EXECUTIVE ACTION COPILOT — INTERACTIVE SESSION")
        print(f"Executive: {brief.executive_name} ({brief.executive_role})")
        print(f"Reference Date: {target_date.strftime('%A, %d %B %Y')}")
        print("Commands: 'brief', 'my actions', 'waiting', 'unclear', 'quit' or ask any question.")
        print("=" * 75 + "\n")

        while True:
            try:
                user_input = input("\nArjun [Copilot]> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Copilot.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Session closed.")
                break
            if user_input.lower() == "brief":
                md = copilot.brief_generator.render_markdown(brief, include_evidence=not args.no_evidence)
                print("\n" + md)
                continue

            res = copilot.ask(user_input)
            print("\n" + res["answer"])
            if res.get("evidence"):
                print("\n[Source Evidence]:")
                for e in res["evidence"]:
                    print(f"  • {e}")
        return

    # Default: Output the daily brief in Markdown
    md_output = copilot.brief_generator.render_markdown(brief, include_evidence=not args.no_evidence)
    print(md_output)


if __name__ == "__main__":
    main()
