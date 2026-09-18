"""Deduplicator for Executive Action Copilot.

Clusters multiple action mentions across emails, transcripts, and voice notes
into single canonical action clusters keyed by deliverable topic.
"""
from typing import List, Dict
from models import ActionMention


TOPIC_METADATA = {
    "vendor_list": {
        "title": "Send updated vendor list to Raghav Sethi",
        "default_owner": "Arjun Malhotra",
        "default_counterparty": "Raghav Sethi",
    },
    "campaign_deck": {
        "title": "Review Q3 Campaign Deck with Neha Kapoor",
        "default_owner": "Arjun Malhotra",
        "default_counterparty": "Neha Kapoor",
    },
    "meridian_call": {
        "title": "Reschedule and hold client call with Meridian Logistics (Priya Nair)",
        "default_owner": "Arjun Malhotra",
        "default_counterparty": "Priya Nair",
    },
    "expense_report": {
        "title": "Obtain and review July Expense Variance Report from Divya Rao",
        "default_owner": "Divya Rao",
        "default_counterparty": "Arjun Malhotra",
    },
    "mumbai_lease": {
        "title": "Authorize & sign Mumbai office lease renewal paperwork",
        "default_owner": "Unassigned / Needs Owner",
        "default_counterparty": "Facilities",
    },
}


class Deduplicator:
    def group_by_topic(self, mentions: List[ActionMention]) -> Dict[str, List[ActionMention]]:
        """Groups mentions into canonical deliverable clusters, sorted chronologically."""
        clusters: Dict[str, List[ActionMention]] = {}
        for m in mentions:
            clusters.setdefault(m.topic_key, []).append(m)

        # Sort each cluster chronologically
        for topic, topic_mentions in clusters.items():
            topic_mentions.sort(key=lambda m: m.evidence.timestamp)

        return clusters

    def get_cluster_metadata(self, topic_key: str) -> Dict[str, str]:
        return TOPIC_METADATA.get(
            topic_key,
            {
                "title": f"Deliverable: {topic_key}",
                "default_owner": "Unknown",
                "default_counterparty": None,
            },
        )
