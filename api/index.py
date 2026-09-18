"""Vercel Serverless Function entry point for Executive Action Copilot."""
import os
import sys
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from datetime import datetime, date

# Ensure root directory is in sys.path so modules can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from copilot import ExecutiveActionCopilot
from models import ReconciledAction, DailyBrief


def action_to_dict(a: ReconciledAction):
    return {
        "action_id": a.action_id,
        "topic_key": a.topic_key,
        "title": a.title,
        "owner": a.owner,
        "counterparty": a.counterparty,
        "ownership_category": a.ownership_category.value,
        "reconciled_deadline_str": a.reconciled_deadline_str,
        "action_status": a.action_status.value,
        "urgency_status": a.urgency_status.value,
        "summary_of_progression": a.summary_of_progression,
        "notes_or_risks": a.notes_or_risks,
        "evidence_trail": [
            {
                "source_type": e.source_type.value,
                "source_label": e.source_label,
                "timestamp_str": e.timestamp_str,
                "sender_or_speaker": e.sender_or_speaker,
                "recipient": e.recipient,
                "excerpt": e.excerpt,
                "citation": e.format_citation(),
            }
            for e in a.evidence_trail
        ],
    }


def brief_to_dict(brief: DailyBrief):
    return {
        "target_date": brief.target_date.strftime("%Y-%m-%d"),
        "target_date_formatted": brief.target_date.strftime("%A, %d %B %Y"),
        "executive_name": brief.executive_name,
        "executive_role": brief.executive_role,
        "my_actions": [action_to_dict(a) for a in brief.my_actions],
        "waiting_on_others": [action_to_dict(a) for a in brief.waiting_on_others],
        "unclear_ownership": [action_to_dict(a) for a in brief.unclear_ownership],
        "agent_activity": [
            {
                "step_name": l.step_name,
                "description": l.description,
                "count_summary": l.count_summary,
                "log_text": l.format_log(),
            }
            for l in brief.agent_activity
        ],
        "calendar_events_today": brief.calendar_events_today,
    }


# Cache copilot instance per target date
COPILOT_INSTANCES = {}


def get_copilot_for_date(target_date: date) -> ExecutiveActionCopilot:
    if target_date not in COPILOT_INSTANCES:
        copilot = ExecutiveActionCopilot(default_reference_date=target_date)
        copilot.run_pipeline(as_of_dt=datetime.combine(target_date, datetime.min.time().replace(hour=9, minute=0)))
        COPILOT_INSTANCES[target_date] = copilot
    return COPILOT_INSTANCES[target_date]


class handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.endswith("/brief") or path == "/api/brief":
            query_params = urllib.parse.parse_qs(parsed.query)
            date_param = query_params.get("date", ["2026-09-25"])[0]
            try:
                target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            except ValueError:
                target_date = date(2026, 9, 25)

            copilot = get_copilot_for_date(target_date)
            brief = copilot.latest_brief
            self._send_json(brief_to_dict(brief))
            return

        if path.endswith("/dates") or path == "/api/dates":
            dates = [
                {"date": "2026-09-21", "label": "Mon 21 Sep"},
                {"date": "2026-09-22", "label": "Tue 22 Sep"},
                {"date": "2026-09-23", "label": "Wed 23 Sep"},
                {"date": "2026-09-24", "label": "Thu 24 Sep"},
                {"date": "2026-09-25", "label": "Fri 25 Sep"},
            ]
            self._send_json({"available_dates": dates, "default_date": "2026-09-25"})
            return

        self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.endswith("/ask") or path == "/api/ask":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)
            try:
                payload = json.loads(post_body.decode("utf-8"))
            except Exception:
                self._send_json({"error": "Invalid JSON"}, 400)
                return

            query = payload.get("query", "").strip()
            date_param = payload.get("date", "2026-09-25")
            try:
                target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            except ValueError:
                target_date = date(2026, 9, 25)

            if not query:
                self._send_json({"error": "Empty query"}, 400)
                return

            copilot = get_copilot_for_date(target_date)
            answer_data = copilot.ask(query)
            self._send_json(answer_data)
            return

        self.send_error(404, "Endpoint Not Found")
