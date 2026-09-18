"""Daily Action Brief Generator for Executive Action Copilot.

Produces structured, executive-level daily briefs for Arjun Malhotra (VP Sales)
categorized by Ownership and Timeline, with high-level Agent Activity logging and source evidence citations.
"""
from datetime import datetime, date
from typing import List, Dict, Any

from models import (
    ReconciledAction,
    OwnershipCategory,
    UrgencyStatus,
    AgentActivityLog,
    DailyBrief,
)
from data_pack import get_calendar_events


class BriefGenerator:
    def __init__(self, executive_name: str = "Arjun Malhotra", executive_role: str = "VP Sales"):
        self.executive_name = executive_name
        self.executive_role = executive_role

    def generate_brief_data(
        self,
        actions: List[ReconciledAction],
        agent_activity: List[AgentActivityLog],
        target_date: date,
    ) -> DailyBrief:
        # Categorize actions by ownership
        my_actions = [a for a in actions if a.ownership_category == OwnershipCategory.MY_ACTIONS]
        waiting_on_others = [a for a in actions if a.ownership_category == OwnershipCategory.WAITING_ON_OTHERS]
        unclear_ownership = [a for a in actions if a.ownership_category == OwnershipCategory.UNCLEAR_OWNERSHIP]

        # Gather calendar events for target date
        cal_events = []
        for ev in get_calendar_events():
            if ev.person_name == self.executive_name and ev.event_date == target_date:
                cal_events.append({
                    "time": ev.time_range_str,
                    "event": ev.event_title,
                })

        return DailyBrief(
            target_date=target_date,
            generated_at=datetime.now(),
            executive_name=self.executive_name,
            executive_role=self.executive_role,
            my_actions=my_actions,
            waiting_on_others=waiting_on_others,
            unclear_ownership=unclear_ownership,
            agent_activity=agent_activity,
            calendar_events_today=cal_events,
        )

    def render_markdown(self, brief: DailyBrief, include_evidence: bool = True) -> str:
        lines = []
        date_str = brief.target_date.strftime("%A, %d %B %Y")
        lines.append(f"# Executive Action Copilot — Daily Brief")
        lines.append(f"**Target Date:** {date_str} | **Executive:** {brief.executive_name} ({brief.executive_role})")
        lines.append(f"**Status Snapshot:** Verified from Meeting Transcripts, Email Threads, Calendars & Voice Notes")
        lines.append("-" * 75)

        # Agent Activity Section (High-level summary, no CoT)
        lines.append("## [AGENT ACTIVITY] System Execution Log")
        lines.append("*High-level execution summary of ingestion, deduplication, and reconciliation:*")
        for act in brief.agent_activity:
            lines.append(f"- {act.format_log()}")
        lines.append("")

        # Today's Calendar Schedule
        if brief.calendar_events_today:
            lines.append("## [SCHEDULE] Today's Calendar Schedule")
            for ev in brief.calendar_events_today:
                lines.append(f"- **{ev['time']}**: {ev['event']}")
            lines.append("")

        # Helper to format action item
        def format_action_card(act: ReconciledAction) -> List[str]:
            item_lines = []
            status_badge = f"[{act.urgency_status.value.upper()}]"
            item_lines.append(f"### {status_badge} {act.title}")
            item_lines.append(f"- **Owner:** {act.owner} | **Counterparty:** {act.counterparty or 'N/A'}")
            item_lines.append(f"- **Reconciled Deadline:** {act.reconciled_deadline_str}")
            item_lines.append(f"- **Action Status:** `{act.action_status.value}` | **Urgency:** `{act.urgency_status.value}`")
            item_lines.append(f"- **Progression Summary:** {act.summary_of_progression}")
            if act.notes_or_risks:
                item_lines.append(f"- **[NOTICE / RISK]:** {act.notes_or_risks}")
            if include_evidence and act.evidence_trail:
                item_lines.append("- **Source Evidence Trail:**")
                for ev in act.evidence_trail:
                    item_lines.append(f"  * {ev.format_citation()}")
            item_lines.append("")
            return item_lines

        # Section 1: My Actions
        lines.append("## 1. My Actions (Arjun Malhotra)")
        if not brief.my_actions:
            lines.append("_No pending actions assigned to you._\n")
        else:
            # Sort by urgency priority: Overdue -> Due Today -> Upcoming -> Completed
            urgency_order = {
                UrgencyStatus.OVERDUE: 0,
                UrgencyStatus.DUE_TODAY: 1,
                UrgencyStatus.UPCOMING: 2,
                UrgencyStatus.COMPLETED: 3,
            }
            sorted_my_actions = sorted(brief.my_actions, key=lambda a: urgency_order.get(a.urgency_status, 99))
            for act in sorted_my_actions:
                lines.extend(format_action_card(act))

        # Section 2: Waiting on Others
        lines.append("## 2. Waiting on Others")
        if not brief.waiting_on_others:
            lines.append("_No outstanding items waiting on others._\n")
        else:
            for act in brief.waiting_on_others:
                lines.extend(format_action_card(act))

        # Section 3: Unclear Ownership
        lines.append("## 3. Unclear Ownership (Flagged — Not Guessed)")
        if not brief.unclear_ownership:
            lines.append("_No items with unclear ownership._\n")
        else:
            for act in brief.unclear_ownership:
                lines.extend(format_action_card(act))

        return "\n".join(lines)
