"""Main Executive Action Copilot Orchestrator.

Implements the complete core flow:
Extract → Deduplicate → Reconcile latest state → Ownership/deadline/status → Evidence → Daily Brief → Q&A
Maintains high-level Agent Activity logging (no internal chain of thought).
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from models import (
    ActionMention,
    ReconciledAction,
    AgentActivityLog,
    DailyBrief,
)
from extractor import RuleBasedExtractor
from deduplicator import Deduplicator
from reconciler import ActionReconciler
from brief_generator import BriefGenerator
from qa_engine import QAEngine
from data_pack import (
    get_meeting_transcripts,
    get_email_threads,
    get_voice_notes,
    get_calendar_events,
)


class ExecutiveActionCopilot:
    def __init__(
        self,
        executive_name: str = "Arjun Malhotra",
        executive_role: str = "VP Sales",
        default_reference_date: date = date(2026, 9, 25),
    ):
        self.executive_name = executive_name
        self.executive_role = executive_role
        self.reference_date = default_reference_date

        self.extractor = RuleBasedExtractor()
        self.deduplicator = Deduplicator()
        self.reconciler = ActionReconciler(executive_name=self.executive_name)
        self.brief_generator = BriefGenerator(
            executive_name=self.executive_name, executive_role=self.executive_role
        )
        self.qa_engine = QAEngine(executive_name=self.executive_name)

        # Pipeline state
        self.raw_mentions: List[ActionMention] = []
        self.clusters: Dict[str, List[ActionMention]] = {}
        self.reconciled_actions: List[ReconciledAction] = []
        self.agent_activity: List[AgentActivityLog] = []
        self.latest_brief: Optional[DailyBrief] = None

    def run_pipeline(self, as_of_dt: Optional[datetime] = None) -> DailyBrief:
        """Executes the full core pipeline: Extract -> Deduplicate -> Reconcile -> Brief."""
        if as_of_dt is None:
            as_of_dt = datetime.combine(self.reference_date, datetime.min.time().replace(hour=9, minute=0))

        target_date = as_of_dt.date()
        self.agent_activity.clear()

        # Step 1: Ingestion & Extraction
        meetings = get_meeting_transcripts()
        emails = get_email_threads()
        voice_notes = get_voice_notes()
        calendars = get_calendar_events()

        self.agent_activity.append(
            AgentActivityLog(
                step_name="INGEST",
                description=f"Ingested multi-source data: 1 meeting transcript ({len(meetings[0].statements)} statements), 5 email threads ({len(emails)} emails), 4 participant calendars ({len(calendars)} events), and 2 voice notes.",
            )
        )

        self.raw_mentions = self.extractor.extract_all()
        self.agent_activity.append(
            AgentActivityLog(
                step_name="EXTRACT",
                description=f"Extracted candidate action mentions, commitments, deadline signals, and ownership cues using rule-based parsing.",
                count_summary=f"{len(self.raw_mentions)} mentions identified",
            )
        )

        # Step 2: Deduplication & Semantic Clustering
        self.clusters = self.deduplicator.group_by_topic(self.raw_mentions)
        cluster_names = ", ".join(self.clusters.keys())
        self.agent_activity.append(
            AgentActivityLog(
                step_name="DEDUPLICATE",
                description=f"Deduplicated cross-source mentions into canonical deliverable clusters ({cluster_names}).",
                count_summary=f"{len(self.clusters)} distinct deliverables",
            )
        )

        # Step 3: Chronological State & Deadline Reconciliation
        self.reconciled_actions = self.reconciler.reconcile_all(self.clusters, as_of_dt)
        self.agent_activity.append(
            AgentActivityLog(
                step_name="RECONCILE",
                description=f"Reconciled chronological state progression, updated deadline shifts, and strictly assigned ownership.",
                count_summary=f"As of {as_of_dt.strftime('%A, %d %b %Y %I:%M %p')}",
            )
        )

        # Step 4: Verification & Categorization
        my_acts = sum(1 for a in self.reconciled_actions if a.ownership_category.value == "My Actions")
        waiting = sum(1 for a in self.reconciled_actions if a.ownership_category.value == "Waiting on Others")
        unclear = sum(1 for a in self.reconciled_actions if a.ownership_category.value == "Unclear Ownership")

        self.agent_activity.append(
            AgentActivityLog(
                step_name="CLASSIFY",
                description=f"Partitioned deliverables strictly without guessing: My Actions ({my_acts}), Waiting on Others ({waiting}), Unclear Ownership ({unclear}).",
            )
        )

        # Step 5: Daily Brief Generation
        self.latest_brief = self.brief_generator.generate_brief_data(
            actions=self.reconciled_actions,
            agent_activity=list(self.agent_activity),
            target_date=target_date,
        )
        self.agent_activity.append(
            AgentActivityLog(
                step_name="BRIEF_READY",
                description=f"Generated executive daily brief for {target_date.strftime('%A %d %b %Y')}.",
            )
        )

        return self.latest_brief

    def ask(self, question: str) -> Dict[str, Any]:
        """Queries the Q&A Engine using the reconciled action state."""
        if not self.reconciled_actions:
            self.run_pipeline()

        result = self.qa_engine.answer_query(
            query=question,
            actions=self.reconciled_actions,
            target_date=self.reference_date,
            brief=self.latest_brief,
        )

        self.agent_activity.append(
            AgentActivityLog(
                step_name="Q&A",
                description=f"Answered user question '{question}' with intent {result['matched_intent']}.",
            )
        )
        return result
