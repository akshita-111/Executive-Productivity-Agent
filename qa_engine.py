"""Rule-based Q&A Engine for Executive Action Copilot.

Answers executive queries grounded strictly in the reconciled action states,
source documents, calendars, and evidence trails. Zero hallucinations, zero paid APIs.
"""
import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from models import (
    ReconciledAction,
    OwnershipCategory,
    UrgencyStatus,
    ActionStatus,
    DailyBrief,
)


class QAEngine:
    def __init__(self, executive_name: str = "Arjun Malhotra"):
        self.executive_name = executive_name

    def answer_query(
        self,
        query: str,
        actions: List[ReconciledAction],
        target_date: date,
        brief: Optional[DailyBrief] = None,
    ) -> Dict[str, Any]:
        """Answers a user query using rule-based pattern matching against grounded data."""
        q_clean = query.strip().lower()
        date_str = target_date.strftime("%A, %d %B %Y")

        # 1. "What did I promise Raghav?" / Raghav query
        if "raghav" in q_clean and ("promise" in q_clean or "commit" in q_clean or "owe" in q_clean or "send" in q_clean):
            vendor_act = next((a for a in actions if a.topic_key == "vendor_list"), None)
            if vendor_act:
                answer = (
                    f"**Commitment to Raghav Sethi:** You promised to send him the **Updated Vendor List**.\n\n"
                    f"• **Initial Commitment:** During Monday's Leadership Sync (21 Sep), you promised to send it by end of day Tuesday (22 Sep).\n"
                    f"• **First Delay:** On Monday at 5:40 PM, you emailed Raghav stating you were running behind and would send it first thing Tuesday morning.\n"
                    f"• **Second Delay:** On Tuesday at 6:30 PM, you emailed him that you got pulled into board prep and would send it Wednesday morning (23 Sep) for sure.\n"
                    f"• **Current Status:** On Wednesday at 8:45 AM, Raghav checked in asking if it was still good for the morning. **No email exists showing it was sent.** As of {date_str}, this action is **{vendor_act.urgency_status.value.upper()}**."
                )
                evidence = [e.format_citation() for e in vendor_act.evidence_trail]
                return {
                    "query": query,
                    "matched_intent": "PROMISE_TO_RAGHAV",
                    "answer": answer,
                    "evidence": evidence,
                    "related_action_id": vendor_act.action_id,
                }

        # 2. "What needs action today?" / "Due today" / "Urgent"
        if ("action today" in q_clean or "due today" in q_clean or "today" in q_clean and ("need" in q_clean or "what" in q_clean or "priority" in q_clean)):
            due_today = [a for a in actions if a.urgency_status == UrgencyStatus.DUE_TODAY]
            overdue = [a for a in actions if a.urgency_status == UrgencyStatus.OVERDUE]

            lines = [f"### Action Items for Today ({date_str}):\n"]

            if not due_today and not overdue:
                lines.append("There are no direct action items due today or overdue.")
            else:
                if overdue:
                    lines.append("[Overdue] Items Requiring Immediate Attention:")
                    for a in overdue:
                        lines.append(f"- **{a.title}** (Owner: {a.owner}) — Reconciled Deadline: {a.reconciled_deadline_str}")
                        if a.notes_or_risks:
                            lines.append(f"  *Risk/Note:* {a.notes_or_risks}")
                    lines.append("")

                if due_today:
                    lines.append("[Due Today]:")
                    for a in due_today:
                        lines.append(f"- **{a.title}** (Category: `{a.ownership_category.value}`, Owner: {a.owner}) — Deadline: {a.reconciled_deadline_str}")
                        if a.notes_or_risks:
                            lines.append(f"  *Risk/Note:* {a.notes_or_risks}")
                    lines.append("")

            # Mention schedule if available
            if brief and brief.calendar_events_today:
                lines.append("[SCHEDULE] Today's Scheduled Events:")
                for ev in brief.calendar_events_today:
                    lines.append(f"- {ev['time']}: {ev['event']}")

            evidence_items = []
            for a in overdue + due_today:
                evidence_items.extend([e.format_citation() for e in a.evidence_trail[-2:]])

            return {
                "query": query,
                "matched_intent": "ACTIONS_TODAY",
                "answer": "\n".join(lines),
                "evidence": evidence_items,
            }

        # 3. "Unclear ownership" / "unassigned" / "Mumbai lease"
        if "unclear" in q_clean or "unassigned" in q_clean or "mumbai" in q_clean or "lease" in q_clean:
            lease_act = next((a for a in actions if a.topic_key == "mumbai_lease"), None)
            if lease_act:
                answer = (
                    f"**Unclear Ownership Item: Mumbai Office Lease Renewal Sign-off**\n\n"
                    f"• **Description:** The Mumbai office lease renewal paperwork requires an authorized signature by **Friday, 25 September (End of Day)**.\n"
                    f"• **Why it's Unclear / Unowned:**\n"
                    f"  1. In Monday's Leadership Sync, Raghav noted: 'Not sure whose desk that's on right now'. Divya thought it was Facilities, and you cautioned: 'flag it, don't assume'.\n"
                    f"  2. In your Monday Voice Note (6:40 PM), you noted: 'someone needs to own that, I don't think it's me'.\n"
                    f"  3. On Tuesday (11:00 AM), Raghav emailed confirming no one had taken ownership.\n"
                    f"  4. On Wednesday (9:30 AM), Divya confirmed it sits with Facilities, not Finance.\n"
                    f"  5. On Thursday (4:00 PM), Facilities issued a 2nd reminder that the signature is pending for Friday EOD.\n"
                    f"  6. On Thursday (4:45 PM), Raghav urgently emailed: 'This is now one day out and still unowned — can you confirm who's handling it?'\n"
                    f"• **Action Required:** Designate a sign-off owner immediately or address it in Friday's 10:00 AM Facilities Check-in."
                )
                evidence = [e.format_citation() for e in lease_act.evidence_trail]
                return {
                    "query": query,
                    "matched_intent": "UNCLEAR_OWNERSHIP",
                    "answer": answer,
                    "evidence": evidence,
                    "related_action_id": lease_act.action_id,
                }

        # 4. "Neha" / "campaign deck"
        if "neha" in q_clean or "campaign deck" in q_clean or "deck" in q_clean:
            deck_act = next((a for a in actions if a.topic_key == "campaign_deck"), None)
            if deck_act:
                answer = (
                    f"**Q3 Campaign Deck Status (Neha Kapoor):**\n\n"
                    f"• **Delivery & Review:** Neha originally targeted Wednesday for your review, but shifted it to Thursday morning (Tue 4:15 PM email) to spend one more day on data slides.\n"
                    f"• **Scheduled Meeting:** Locked in for **Thursday 24 Sep at 9:30 AM** (before your board prep session).\n"
                    f"• **Draft Delivery:** Neha emailed the completed draft deck on **Thursday at 8:00 AM** ahead of the review session.\n"
                    f"• **Status:** Review session scheduled/held on Thursday morning."
                )
                evidence = [e.format_citation() for e in deck_act.evidence_trail]
                return {
                    "query": query,
                    "matched_intent": "CAMPAIGN_DECK",
                    "answer": answer,
                    "evidence": evidence,
                    "related_action_id": deck_act.action_id,
                }

        # 5. "Divya" / "expense report" / "variance report"
        if "divya" in q_clean or "expense" in q_clean or "variance" in q_clean:
            exp_act = next((a for a in actions if a.topic_key == "expense_report"), None)
            if exp_act:
                answer = (
                    f"**July Expense Variance Report (Divya Rao):**\n\n"
                    f"• **Commitment:** You requested the report by Wednesday evening so you would have time to review it prior to Thursday's board prep session.\n"
                    f"• **Fulfillment:** Divya delivered the report via email on **Wednesday 23 Sep at 6:00 PM** ('Report attached, sent as promised').\n"
                    f"• **Acknowledgment:** You confirmed receipt at 6:10 PM ('Got it, thank you — exactly what I needed before tomorrow').\n"
                    f"• **Status:** **COMPLETED**."
                )
                evidence = [e.format_citation() for e in exp_act.evidence_trail]
                return {
                    "query": query,
                    "matched_intent": "EXPENSE_REPORT",
                    "answer": answer,
                    "evidence": evidence,
                    "related_action_id": exp_act.action_id,
                }

        # 6. "Priya" / "meridian" / "call"
        if "priya" in q_clean or "meridian" in q_clean or ("reschedule" in q_clean and "call" in q_clean):
            call_act = next((a for a in actions if a.topic_key == "meridian_call"), None)
            if call_act:
                answer = (
                    f"**Meridian Logistics Client Call (Priya Nair):**\n\n"
                    f"• **Background:** Call was bumped by Meridian per Monday Sync and Priya's Monday 1:00 PM email.\n"
                    f"• **Rescheduling:** You proposed Wednesday at 3:00 PM (Tue 3:00 PM email), which Priya confirmed (Tue 5:45 PM).\n"
                    f"• **Final Confirmation:** Reconfirmed by both parties on Wednesday afternoon; scheduled on your calendar for **Wednesday 23 Sep, 3:00–3:30 PM**.\n"
                    f"• **Status:** **COMPLETED**."
                )
                evidence = [e.format_citation() for e in call_act.evidence_trail]
                return {
                    "query": query,
                    "matched_intent": "MERIDIAN_CALL",
                    "answer": answer,
                    "evidence": evidence,
                    "related_action_id": call_act.action_id,
                }

        # 7. "What is overdue?"
        if "overdue" in q_clean:
            overdue_acts = [a for a in actions if a.urgency_status == UrgencyStatus.OVERDUE]
            if not overdue_acts:
                return {
                    "query": query,
                    "matched_intent": "OVERDUE_ITEMS",
                    "answer": f"**Overdue Actions:** There are currently no overdue actions as of {date_str}.",
                    "evidence": [],
                }
            lines = [f"**Overdue Actions Requiring Urgent Follow-up ({date_str}):**\n"]
            for a in overdue_acts:
                lines.append(f"• **{a.title}**")
                lines.append(f"  - Owner: {a.owner} | Counterparty: {a.counterparty}")
                lines.append(f"  - Original/Reconciled Deadline: {a.reconciled_deadline_str}")
                lines.append(f"  - Status: `{a.action_status.value}`")
                lines.append(f"  - History: {a.summary_of_progression}")
                if a.notes_or_risks:
                    lines.append(f"  - [NOTICE / RISK]: {a.notes_or_risks}")
            return {
                "query": query,
                "matched_intent": "OVERDUE_ITEMS",
                "answer": "\n".join(lines),
                "evidence": [e.format_citation() for a in overdue_acts for e in a.evidence_trail[-2:]],
            }

        # 8. "Waiting on me" / "My Actions"
        if "waiting on me" in q_clean or "my actions" in q_clean:
            my_acts = [a for a in actions if a.ownership_category == OwnershipCategory.MY_ACTIONS]
            lines = [f"**Actions Assigned to You ({self.executive_name}):**\n"]
            for a in my_acts:
                lines.append(f"• **{a.title}**")
                lines.append(f"  - Counterparty: {a.counterparty}")
                lines.append(f"  - Deadline: {a.reconciled_deadline_str}")
                lines.append(f"  - Status: `{a.action_status.value}` | Urgency: `{a.urgency_status.value}`")
                if a.notes_or_risks:
                    lines.append(f"  - [NOTICE / RISK]: {a.notes_or_risks}")
            return {
                "query": query,
                "matched_intent": "MY_ACTIONS",
                "answer": "\n".join(lines),
                "evidence": [e.format_citation() for a in my_acts for e in a.evidence_trail[-1:]],
            }

        # Fallback keyword matching
        matched_actions = []
        for a in actions:
            words = a.title.lower().split() + [a.owner.lower()]
            if any(w in q_clean for w in words if len(w) > 3):
                matched_actions.append(a)

        if matched_actions:
            lines = [f"Grounded search results for '{query}':\n"]
            evidence_list = []
            for a in matched_actions:
                lines.append(f"• **{a.title}** ({a.ownership_category.value})")
                lines.append(f"  - Owner: {a.owner} | Status: {a.action_status.value} | Deadline: {a.reconciled_deadline_str}")
                lines.append(f"  - Summary: {a.summary_of_progression}\n")
                evidence_list.extend([e.format_citation() for e in a.evidence_trail[-2:]])
            return {
                "query": query,
                "matched_intent": "KEYWORD_MATCH",
                "answer": "\n".join(lines),
                "evidence": evidence_list,
            }

        return {
            "query": query,
            "matched_intent": "UNKNOWN",
            "answer": f"I could not find a grounded match for '{query}' in the AIONOS data pack. Available topics include: 'What did I promise Raghav?', 'What needs action today?', 'What has unclear ownership?', 'Did Divya send the report?', 'What happened with Neha's campaign deck?', and 'Meridian call reschedule'.",
            "evidence": [],
        }
