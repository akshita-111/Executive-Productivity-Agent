"""Automated verification suite for Executive Action Copilot."""
import unittest
from datetime import date, datetime

from data_pack import (
    get_meeting_transcripts,
    get_calendar_events,
    get_email_threads,
    get_voice_notes,
)
from extractor import RuleBasedExtractor
from deduplicator import Deduplicator
from reconciler import ActionReconciler
from copilot import ExecutiveActionCopilot
from models import OwnershipCategory, UrgencyStatus, ActionStatus


class TestExecutiveActionCopilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copilot = ExecutiveActionCopilot(default_reference_date=date(2026, 9, 25))
        cls.brief_friday = cls.copilot.run_pipeline(as_of_dt=datetime(2026, 9, 25, 9, 0))

    def test_01_data_pack_counts(self):
        """Verify the raw data pack contains all required sources."""
        transcripts = get_meeting_transcripts()
        self.assertEqual(len(transcripts), 1)
        self.assertEqual(len(transcripts[0].statements), 10)

        emails = get_email_threads()
        self.assertEqual(len(emails), 25)  # 5 threads x 5 emails

        voice_notes = get_voice_notes()
        self.assertEqual(len(voice_notes), 2)

        calendars = get_calendar_events()
        self.assertGreaterEqual(len(calendars), 20)

    def test_02_extraction_and_clustering(self):
        """Verify extraction and deduplication into the 5 core deliverables."""
        extractor = RuleBasedExtractor()
        mentions = extractor.extract_all()
        self.assertGreater(len(mentions), 15)

        dedup = Deduplicator()
        clusters = dedup.group_by_topic(mentions)

        expected_topics = {
            "vendor_list",
            "campaign_deck",
            "meridian_call",
            "expense_report",
            "mumbai_lease",
        }
        self.assertTrue(expected_topics.issubset(set(clusters.keys())))

    def test_03_strict_ownership_partitioning(self):
        """Verify strict ownership without guessing."""
        actions = self.copilot.reconciled_actions
        action_map = {a.topic_key: a for a in actions}

        # My Actions
        self.assertEqual(action_map["vendor_list"].ownership_category, OwnershipCategory.MY_ACTIONS)
        self.assertEqual(action_map["vendor_list"].owner, "Arjun Malhotra")

        self.assertEqual(action_map["campaign_deck"].ownership_category, OwnershipCategory.MY_ACTIONS)
        self.assertEqual(action_map["campaign_deck"].owner, "Arjun Malhotra")

        self.assertEqual(action_map["meridian_call"].ownership_category, OwnershipCategory.MY_ACTIONS)
        self.assertEqual(action_map["meridian_call"].owner, "Arjun Malhotra")

        # Waiting on Others
        self.assertEqual(action_map["expense_report"].ownership_category, OwnershipCategory.WAITING_ON_OTHERS)
        self.assertEqual(action_map["expense_report"].owner, "Divya Rao")

        # Unclear Ownership (Must never guess!)
        self.assertEqual(action_map["mumbai_lease"].ownership_category, OwnershipCategory.UNCLEAR_OWNERSHIP)
        self.assertIn("Unassigned", action_map["mumbai_lease"].owner)

    def test_04_friday_deadline_and_urgency(self):
        """Verify urgency and deadline states as of Friday 25 Sep morning."""
        action_map = {a.topic_key: a for a in self.copilot.reconciled_actions}

        # Vendor list was due Wednesday morning -> Overdue on Friday
        self.assertEqual(action_map["vendor_list"].urgency_status, UrgencyStatus.OVERDUE)
        self.assertEqual(action_map["vendor_list"].action_status, ActionStatus.PENDING)

        # Mumbai lease is due Friday EOD -> Due Today on Friday
        self.assertEqual(action_map["mumbai_lease"].urgency_status, UrgencyStatus.DUE_TODAY)
        self.assertIn("25 Sep", action_map["mumbai_lease"].reconciled_deadline_str)

        # Completed items
        self.assertEqual(action_map["expense_report"].urgency_status, UrgencyStatus.COMPLETED)
        self.assertEqual(action_map["meridian_call"].urgency_status, UrgencyStatus.COMPLETED)
        self.assertEqual(action_map["campaign_deck"].urgency_status, UrgencyStatus.COMPLETED)

    def test_05_wednesday_dynamic_urgency(self):
        """Verify urgency recalculates accurately for Wednesday 23 Sep morning."""
        wed_brief = self.copilot.run_pipeline(as_of_dt=datetime(2026, 9, 23, 8, 30))
        action_map = {a.topic_key: a for a in self.copilot.reconciled_actions}

        # Vendor list is Due Today on Wednesday morning
        self.assertEqual(action_map["vendor_list"].urgency_status, UrgencyStatus.DUE_TODAY)

        # Mumbai lease is Upcoming on Wednesday (due Friday)
        self.assertEqual(action_map["mumbai_lease"].urgency_status, UrgencyStatus.UPCOMING)

    def test_06_evidence_citation_integrity(self):
        """Verify every deliverable has source citations across evidence trail."""
        for act in self.copilot.reconciled_actions:
            self.assertGreaterEqual(
                len(act.evidence_trail),
                2,
                f"Action {act.title} must have at least 2 source citations",
            )
            for ev in act.evidence_trail:
                citation = ev.format_citation()
                self.assertTrue(len(citation) > 10)
                self.assertTrue(ev.source_type.value in citation)

    def test_07_qa_what_did_i_promise_raghav(self):
        """Test required query: 'What did I promise Raghav?'"""
        res = self.copilot.ask("What did I promise Raghav?")
        self.assertEqual(res["matched_intent"], "PROMISE_TO_RAGHAV")
        ans = res["answer"]
        self.assertIn("Updated Vendor List", ans)
        self.assertIn("Tuesday", ans)
        self.assertIn("Wednesday", ans)
        self.assertGreaterEqual(len(res["evidence"]), 2)

    def test_08_qa_what_needs_action_today(self):
        """Test required query: 'What needs action today?'"""
        # Re-run pipeline for Friday 25 Sep
        self.copilot.run_pipeline(as_of_dt=datetime(2026, 9, 25, 9, 0))
        res = self.copilot.ask("What needs action today?")
        self.assertEqual(res["matched_intent"], "ACTIONS_TODAY")
        ans = res["answer"]
        # On Friday, vendor list is overdue and Mumbai lease is due today
        self.assertIn("Overdue", ans)
        self.assertIn("Due Today", ans)
        self.assertIn("Mumbai", ans)

    def test_09_qa_unclear_ownership(self):
        """Test query regarding unclear ownership."""
        res = self.copilot.ask("What items have unclear ownership?")
        self.assertEqual(res["matched_intent"], "UNCLEAR_OWNERSHIP")
        ans = res["answer"]
        self.assertIn("Mumbai Office Lease Renewal", ans)
        self.assertIn("Unowned", ans)

    def test_10_agent_activity_logging(self):
        """Test agent activity entries are concise and lack chain-of-thought."""
        logs = self.copilot.agent_activity
        self.assertGreaterEqual(len(logs), 4)
        for entry in logs:
            text = entry.format_log()
            self.assertTrue(text.startswith("[Agent Activity]"))
            # Ensure no chain of thought markers
            self.assertNotIn("I think", text)
            self.assertNotIn("Let's see", text)
            self.assertNotIn("Maybe", text)


if __name__ == "__main__":
    unittest.main()
