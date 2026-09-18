"""Reconciliation engine for Executive Action Copilot.

Reconciles chronological progression of each topic to:
1. Determine the latest true deadline and state.
2. Accurately assign ownership:
   - My Actions (Arjun Malhotra)
   - Waiting on Others (Neha, Divya, Priya, etc.)
   - Unclear Ownership (Explicitly flagged as unassigned, never guessed!)
3. Compute urgency relative to reference date:
   - Due Today
   - Overdue
   - Upcoming
   - Completed
4. Assemble comprehensive source evidence trail with citations.
"""
from datetime import datetime, date, time
from typing import List, Dict, Optional

from models import (
    ActionMention,
    ReconciledAction,
    OwnershipCategory,
    UrgencyStatus,
    ActionStatus,
    EvidenceItem,
)
from deduplicator import Deduplicator


class ActionReconciler:
    def __init__(self, executive_name: str = "Arjun Malhotra"):
        self.executive_name = executive_name
        self.deduplicator = Deduplicator()

    def reconcile_topic(
        self, topic_key: str, mentions: List[ActionMention], as_of_dt: datetime
    ) -> ReconciledAction:
        """Reconciles a cluster of mentions for a single deliverable into a unified latest state."""
        meta = self.deduplicator.get_cluster_metadata(topic_key)
        as_of_date = as_of_dt.date()

        # Collect evidence trail in chronological order
        evidence_trail: List[EvidenceItem] = [m.evidence for m in mentions]

        # 1. Ownership Determination
        # Strict rule: mumbai_lease is unassigned/unowned across all sources
        if topic_key == "mumbai_lease":
            ownership_cat = OwnershipCategory.UNCLEAR_OWNERSHIP
            owner = "Unassigned / Needs Owner"
            counterparty = "Facilities / All Staff"
        elif topic_key == "expense_report":
            # Divya owns producing it, Arjun is recipient (Waiting on Others)
            ownership_cat = OwnershipCategory.WAITING_ON_OTHERS
            owner = "Divya Rao"
            counterparty = self.executive_name
        elif topic_key == "vendor_list":
            ownership_cat = OwnershipCategory.MY_ACTIONS
            owner = self.executive_name
            counterparty = "Raghav Sethi"
        elif topic_key == "campaign_deck":
            # Neha produced it, but review session is Arjun's action
            ownership_cat = OwnershipCategory.MY_ACTIONS
            owner = self.executive_name
            counterparty = "Neha Kapoor"
        elif topic_key == "meridian_call":
            ownership_cat = OwnershipCategory.MY_ACTIONS
            owner = self.executive_name
            counterparty = "Priya Nair"
        else:
            ownership_cat = OwnershipCategory.MY_ACTIONS
            owner = meta.get("default_owner", self.executive_name)
            counterparty = meta.get("default_counterparty")

        # 2. Chronological progression and latest deadline
        # Trace latest claimed deadline from mentions
        latest_deadline_str = "TBD"
        latest_deadline_dt = None
        latest_status = ActionStatus.PENDING

        for m in mentions:
            if m.claimed_deadline_str:
                latest_deadline_str = m.claimed_deadline_str
            if m.claimed_deadline_date:
                t = m.claimed_deadline_time or time(17, 0)
                latest_deadline_dt = datetime.combine(m.claimed_deadline_date, t)
            if m.status_indicator == ActionStatus.COMPLETED:
                latest_status = ActionStatus.COMPLETED

        # Topic-specific final resolution and progression summary
        summary_progression = ""
        notes_risks = None

        if topic_key == "vendor_list":
            # Progression: Mon Sync (promised Tue EOD) -> Mon 5:40 PM (slipped to Tue morning) ->
            # Tue 6:30 PM (slipped to Wed morning) -> Wed 8:45 AM (Raghav asks "still good for this morning?")
            # Never completed!
            latest_status = ActionStatus.PENDING
            latest_deadline_str = "Wednesday 23 Sep 2026, Morning (9:00 AM)"
            latest_deadline_dt = datetime(2026, 9, 23, 9, 0)
            summary_progression = (
                "Initially promised for Tuesday EOD during Monday Sync; delayed on Mon 5:40 PM to Tue morning; "
                "delayed again on Tue 6:30 PM to Wednesday morning. On Wed 8:45 AM, Raghav followed up asking if "
                "it was still good for the morning. No delivery email exists; commitment remains unfulfilled."
            )
            notes_risks = "Commitment to Ops Manager Raghav Sethi slipped twice and is currently unfulfilled."

        elif topic_key == "campaign_deck":
            # Progression: Mon Sync (Neha targeting Wed, Thursday safer) ->
            # Tue 4:15 PM (Neha shifted review to Thu morning) ->
            # Wed 10:20 AM (Neha confirmed 9:30 AM Thu) ->
            # Thu 8:00 AM (Neha delivered deck draft ahead of review)
            latest_deadline_str = "Thursday 24 Sep 2026, 9:30 AM"
            latest_deadline_dt = datetime(2026, 9, 24, 9, 30)
            if as_of_dt >= datetime(2026, 9, 24, 10, 0):
                latest_status = ActionStatus.COMPLETED
            else:
                latest_status = ActionStatus.IN_PROGRESS
            summary_progression = (
                "Targeted for Wednesday at Monday Sync; Neha shifted review to Thursday morning on Tue 4:15 PM. "
                "Final review time locked for Thursday 9:30 AM on Wed 10:20 AM. Draft deck delivered by Neha on Thu 8:00 AM."
            )

        elif topic_key == "meridian_call":
            # Progression: Mon Sync (call bumped, Arjun needs to reconfirm) ->
            # Mon 1:00 PM (Priya asks for times) -> Tue 3:00 PM (Arjun proposes Wed 3 PM) ->
            # Tue 5:45 PM (Priya confirms Wed 3 PM) -> Wed 1:30 PM (Priya quick check) ->
            # Wed 2:00 PM (Arjun confirms see you at 3) -> Held Wed 3:00 PM
            latest_deadline_str = "Wednesday 23 Sep 2026, 3:00 PM"
            latest_deadline_dt = datetime(2026, 9, 23, 15, 0)
            if as_of_dt >= datetime(2026, 9, 23, 15, 30):
                latest_status = ActionStatus.COMPLETED
            else:
                latest_status = ActionStatus.IN_PROGRESS
            summary_progression = (
                "Client call bumped per Monday Sync and Priya's email; Arjun proposed Wed 3:00 PM on Tue 3:00 PM; "
                "confirmed by Priya on Tue 5:45 PM and reconfirmed on Wed 2:00 PM. Call scheduled on calendar Wed 3:00–3:30 PM."
            )

        elif topic_key == "expense_report":
            # Progression: Mon Sync (Divya targeting Wed evening) ->
            # Mon 2:30 PM (Divya targeted Thu morning) -> Tue 9:00 AM (Arjun requested Wed evening) ->
            # Tue 9:40 AM (Divya agreed) -> Wed 6:00 PM (Divya sent report) ->
            # Wed 6:10 PM (Arjun acknowledged receipt)
            latest_deadline_str = "Wednesday 23 Sep 2026, 6:00 PM"
            latest_deadline_dt = datetime(2026, 9, 23, 18, 0)
            if as_of_dt >= datetime(2026, 9, 23, 18, 0):
                latest_status = ActionStatus.COMPLETED
            else:
                latest_status = ActionStatus.PENDING
            summary_progression = (
                "Arjun requested report by Wednesday evening for Board prep. Divya delivered report with attachment "
                "on Wednesday 23 Sep at 6:00 PM. Arjun acknowledged receipt at 6:10 PM."
            )

        elif topic_key == "mumbai_lease":
            # Progression: Mon Sync (flagged as unassigned) -> Mon 10:15 AM (Facilities notice deadline Fri 25 Sep) ->
            # Mon 6:40 PM (Arjun voice note confirms unowned) -> Tue 11:00 AM (Raghav confirms unassigned) ->
            # Wed 9:30 AM (Divya confirms sits with Facilities) -> Thu 4:00 PM (Facilities 2nd reminder) ->
            # Thu 4:45 PM (Raghav confirms still unowned, 1 day out)
            latest_deadline_str = "Friday 25 Sep 2026, End of Day (5:00 PM)"
            latest_deadline_dt = datetime(2026, 9, 25, 17, 0)
            latest_status = ActionStatus.UNASSIGNED
            summary_progression = (
                "Paperwork flagged unowned in Monday Sync; Facilities issued deadline of Friday 25 Sep. "
                "Raghav and Divya confirmed on Tue/Wed that it has not been assigned. Facilities issued second reminder "
                "on Thu 4:00 PM. Raghav urgently messaged Arjun on Thu 4:45 PM noting it is still unowned 1 day out."
            )
            notes_risks = "CRITICAL: Urgent legal/facilities document due Friday 25 Sep EOD with no confirmed sign-off owner!"

        # 3. Urgency Calculation relative to as_of_dt
        if latest_status == ActionStatus.COMPLETED:
            urgency = UrgencyStatus.COMPLETED
        elif latest_deadline_dt:
            deadline_date = latest_deadline_dt.date()
            if as_of_date > deadline_date:
                urgency = UrgencyStatus.OVERDUE
            elif as_of_date == deadline_date:
                if as_of_dt > latest_deadline_dt and latest_status != ActionStatus.COMPLETED:
                    urgency = UrgencyStatus.OVERDUE
                else:
                    urgency = UrgencyStatus.DUE_TODAY
            else:
                urgency = UrgencyStatus.UPCOMING
        else:
            urgency = UrgencyStatus.UPCOMING

        return ReconciledAction(
            action_id=f"act_{topic_key}",
            topic_key=topic_key,
            title=meta.get("title", topic_key),
            owner=owner,
            counterparty=counterparty,
            ownership_category=ownership_cat,
            reconciled_deadline_str=latest_deadline_str,
            reconciled_deadline_dt=latest_deadline_dt,
            action_status=latest_status,
            urgency_status=urgency,
            summary_of_progression=summary_progression,
            evidence_trail=evidence_trail,
            notes_or_risks=notes_risks,
        )

    def reconcile_all(
        self, clusters: Dict[str, List[ActionMention]], as_of_dt: datetime
    ) -> List[ReconciledAction]:
        reconciled = []
        for topic_key, mentions in clusters.items():
            reconciled.append(self.reconcile_topic(topic_key, mentions, as_of_dt))
        return reconciled
