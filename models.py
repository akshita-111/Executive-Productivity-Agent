"""Data models for Executive Action Copilot."""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import List, Optional, Dict, Any


class OwnershipCategory(str, Enum):
    MY_ACTIONS = "My Actions"
    WAITING_ON_OTHERS = "Waiting on Others"
    UNCLEAR_OWNERSHIP = "Unclear Ownership"


class UrgencyStatus(str, Enum):
    DUE_TODAY = "Due Today"
    OVERDUE = "Overdue"
    UPCOMING = "Upcoming"
    COMPLETED = "Completed"


class ActionStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    UNASSIGNED = "Unassigned"


class SourceType(str, Enum):
    MEETING_TRANSCRIPT = "Meeting Transcript"
    EMAIL = "Email"
    CALENDAR = "Calendar"
    VOICE_NOTE = "Voice Note"


@dataclass
class EvidenceItem:
    source_type: SourceType
    source_label: str  # e.g., "Leadership Sync (Mon 21 Sep, 9:00 AM)" or "Email Thread 1, Email #4"
    timestamp_str: str  # e.g., "Mon 21 Sep 2026, 9:00 AM"
    timestamp: datetime
    sender_or_speaker: str
    recipient: Optional[str]
    excerpt: str

    def format_citation(self) -> str:
        if self.recipient:
            return f"[{self.source_type.value}] {self.source_label} ({self.timestamp_str}) - {self.sender_or_speaker} -> {self.recipient}: \"{self.excerpt}\""
        return f"[{self.source_type.value}] {self.source_label} ({self.timestamp_str}) - {self.sender_or_speaker}: \"{self.excerpt}\""


@dataclass
class ActionMention:
    mention_id: str
    topic_key: str  # e.g. "vendor_list", "campaign_deck", "meridian_call", "expense_report", "mumbai_lease"
    description: str
    owner: Optional[str]
    counterparty: Optional[str]
    claimed_deadline_str: Optional[str]
    claimed_deadline_date: Optional[date]
    claimed_deadline_time: Optional[time]
    evidence: EvidenceItem
    status_indicator: ActionStatus = ActionStatus.PENDING
    is_unassigned_flag: bool = False


@dataclass
class ReconciledAction:
    action_id: str
    topic_key: str
    title: str
    owner: str  # "Arjun Malhotra", specific person, or "Unassigned / Needs Owner"
    counterparty: Optional[str]
    ownership_category: OwnershipCategory
    reconciled_deadline_str: str
    reconciled_deadline_dt: Optional[datetime]
    action_status: ActionStatus
    urgency_status: UrgencyStatus
    summary_of_progression: str
    evidence_trail: List[EvidenceItem] = field(default_factory=list)
    notes_or_risks: Optional[str] = None


@dataclass
class AgentActivityLog:
    step_name: str
    description: str
    count_summary: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def format_log(self) -> str:
        if self.count_summary:
            return f"[Agent Activity] [{self.step_name}] {self.description} ({self.count_summary})"
        return f"[Agent Activity] [{self.step_name}] {self.description}"


@dataclass
class DailyBrief:
    target_date: date
    generated_at: datetime
    executive_name: str
    executive_role: str
    my_actions: List[ReconciledAction] = field(default_factory=list)
    waiting_on_others: List[ReconciledAction] = field(default_factory=list)
    unclear_ownership: List[ReconciledAction] = field(default_factory=list)
    agent_activity: List[AgentActivityLog] = field(default_factory=list)
    calendar_events_today: List[Dict[str, Any]] = field(default_factory=list)
