"""Rule-based extractor for Executive Action Copilot.

Extracts action mentions, deadlines, commitments, and ownership cues from:
- Meeting transcripts
- Email threads
- Calendars
- Voice notes
"""
import re
from datetime import datetime, date, time
from typing import List, Optional, Tuple

from models import ActionMention, EvidenceItem, SourceType, ActionStatus
from data_pack import (
    RawMeetingTranscript,
    RawCalendarEvent,
    RawEmail,
    RawVoiceNote,
    get_meeting_transcripts,
    get_calendar_events,
    get_email_threads,
    get_voice_notes,
)

TOPIC_PATTERNS = {
    "vendor_list": [r"vendor\s*list", r"vendors?"],
    "campaign_deck": [r"campaign\s*deck", r"q3\s*deck", r"deck review", r"data slides", r"draft"],
    "meridian_call": [r"meridian(\s*logistics)?", r"client call", r"call reschedule", r"priya"],
    "expense_report": [r"expense(\s*variance)?(\s*report)?", r"variance numbers?", r"july expense"],
    "mumbai_lease": [r"mumbai(\s*office)?(\s*lease)?(\s*renewal)?", r"renewal paperwork", r"lease renewal"],
}

UNASSIGNED_CUES = [
    r"not sure whose desk",
    r"haven't seen anyone pick it up",
    r"flag it,\s*don't assume",
    r"someone needs to own that,\s*i don't think it's me",
    r"don't think it's been assigned",
    r"not on my end",
    r"signature is still pending",
    r"still unowned",
    r"needs someone to sign off",
]

COMPLETION_CUES = [
    r"report attached,\s*sent as promised",
    r"got it,\s*thank you",
    r"yes,\s*confirmed,\s*see you at 3",
    r"wednesday 3 pm works on our end,\s*confirmed",
    r"deck is ready,\s*attaching the draft",
]


def detect_topic(text: str, subject: str = "") -> Optional[str]:
    combined = f"{subject} {text}".lower()
    for topic_key, patterns in TOPIC_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined, re.IGNORECASE):
                return topic_key
    return None


def detect_unassigned(text: str) -> bool:
    low = text.lower()
    return any(re.search(cue, low, re.IGNORECASE) for cue in UNASSIGNED_CUES)


def detect_completion(text: str) -> bool:
    low = text.lower()
    return any(re.search(cue, low, re.IGNORECASE) for cue in COMPLETION_CUES)


def parse_deadline_hints(text: str, base_date: date) -> Tuple[Optional[str], Optional[date], Optional[time]]:
    low = text.lower()
    claimed_str = None
    target_date = None
    target_time = None

    # Date references in week 21-25 Sep 2026
    # Mon = 21, Tue = 22, Wed = 23, Thu = 24, Fri = 25
    if "friday" in low or "25 september" in low or "25 sep" in low:
        claimed_str = "Friday, 25 Sep 2026 (End of Day)"
        target_date = date(2026, 9, 25)
        target_time = time(17, 0)
    elif "thursday morning" in low or "thursday, before your board prep" in low or "9:30 review" in low or "9:30 am thursday" in low:
        claimed_str = "Thursday 24 Sep 2026, 9:30 AM"
        target_date = date(2026, 9, 24)
        target_time = time(9, 30)
    elif "thursday" in low:
        claimed_str = "Thursday 24 Sep 2026"
        target_date = date(2026, 9, 24)
    elif "wednesday 3" in low or "wednesday 3:00 pm" in low or "3 pm today" in low or "at 3" in low:
        claimed_str = "Wednesday 23 Sep 2026, 3:00 PM"
        target_date = date(2026, 9, 23)
        target_time = time(15, 0)
    elif "wednesday evening" in low:
        claimed_str = "Wednesday 23 Sep 2026, Evening (6:00 PM)"
        target_date = date(2026, 9, 23)
        target_time = time(18, 0)
    elif "wednesday morning" in low or "this morning" in low and base_date.day == 23:
        claimed_str = "Wednesday 23 Sep 2026, Morning (9:00 AM)"
        target_date = date(2026, 9, 23)
        target_time = time(9, 0)
    elif "wednesday" in low:
        claimed_str = "Wednesday 23 Sep 2026"
        target_date = date(2026, 9, 23)
    elif "tomorrow morning" in low:
        if base_date == date(2026, 9, 21):
            claimed_str = "Tuesday 22 Sep 2026, Morning"
            target_date = date(2026, 9, 22)
            target_time = time(9, 0)
        elif base_date == date(2026, 9, 22):
            claimed_str = "Wednesday 23 Sep 2026, Morning"
            target_date = date(2026, 9, 23)
            target_time = time(9, 0)
    elif "end of day tomorrow" in low:
        if base_date == date(2026, 9, 21):
            claimed_str = "Tuesday 22 Sep 2026, End of Day"
            target_date = date(2026, 9, 22)
            target_time = time(17, 0)
    elif "today" in low:
        claimed_str = f"{base_date.strftime('%A %d %b %Y')}"
        target_date = base_date

    return claimed_str, target_date, target_time


class RuleBasedExtractor:
    def __init__(self):
        self.executive_name = "Arjun Malhotra"

    def extract_from_meeting(self, meeting: RawMeetingTranscript) -> List[ActionMention]:
        mentions = []
        for idx, stmt in enumerate(meeting.statements):
            topic = detect_topic(stmt.text)
            if not topic:
                continue

            is_unassigned = detect_unassigned(stmt.text)
            claimed_str, d_date, d_time = parse_deadline_hints(stmt.text, meeting.meeting_date)
            
            # Determine preliminary owner / counterparty
            owner = None
            counterparty = None

            if topic == "vendor_list":
                if "told raghav i'd send" in stmt.text.lower() or "i'll get that to him" in stmt.text.lower():
                    owner = "Arjun Malhotra"
                    counterparty = "Raghav Sethi"
            elif topic == "campaign_deck":
                if "i'll send it to arjun" in stmt.text.lower() or stmt.speaker == "Neha Kapoor":
                    owner = "Neha Kapoor"
                    counterparty = "Arjun Malhotra"
            elif topic == "expense_report":
                if "divya, can you" in stmt.text.lower() or stmt.speaker == "Divya Rao":
                    owner = "Divya Rao"
                    counterparty = "Arjun Malhotra"
            elif topic == "meridian_call":
                if "i need to reconfirm" in stmt.text.lower():
                    owner = "Arjun Malhotra"
                    counterparty = "Priya Nair"
            elif topic == "mumbai_lease":
                is_unassigned = True
                owner = None

            evidence = EvidenceItem(
                source_type=SourceType.MEETING_TRANSCRIPT,
                source_label=f"{meeting.meeting_title}",
                timestamp_str=f"Mon 21 Sep 2026, 9:00 AM (statement #{idx+1})",
                timestamp=datetime(2026, 9, 21, 9, 0),
                sender_or_speaker=stmt.speaker,
                recipient=None,
                excerpt=stmt.text,
            )

            mentions.append(ActionMention(
                mention_id=f"meeting_stmt_{idx+1}",
                topic_key=topic,
                description=stmt.text,
                owner=owner,
                counterparty=counterparty,
                claimed_deadline_str=claimed_str,
                claimed_deadline_date=d_date,
                claimed_deadline_time=d_time,
                evidence=evidence,
                status_indicator=ActionStatus.PENDING,
                is_unassigned_flag=is_unassigned,
            ))
        return mentions

    def extract_from_emails(self, emails: List[RawEmail]) -> List[ActionMention]:
        mentions = []
        for em in emails:
            topic = detect_topic(em.body, em.thread_subject)
            if not topic:
                continue

            is_unassigned = detect_unassigned(em.body)
            is_completed = detect_completion(em.body)
            claimed_str, d_date, d_time = parse_deadline_hints(em.body, em.timestamp.date())

            owner = None
            counterparty = None

            if topic == "vendor_list":
                owner = "Arjun Malhotra"
                counterparty = "Raghav Sethi"
            elif topic == "campaign_deck":
                if em.email_index <= 2 or em.email_index == 5:
                    owner = "Neha Kapoor"
                    counterparty = "Arjun Malhotra"
                else:
                    owner = "Arjun Malhotra"
                    counterparty = "Neha Kapoor"
            elif topic == "meridian_call":
                owner = "Arjun Malhotra"
                counterparty = "Priya Nair"
            elif topic == "expense_report":
                owner = "Divya Rao"
                counterparty = "Arjun Malhotra"
            elif topic == "mumbai_lease":
                is_unassigned = True
                owner = None

            status = ActionStatus.COMPLETED if is_completed else ActionStatus.PENDING

            evidence = EvidenceItem(
                source_type=SourceType.EMAIL,
                source_label=f"Thread {em.thread_id} ({em.thread_subject}), Email #{em.email_index}",
                timestamp_str=em.date_str,
                timestamp=em.timestamp,
                sender_or_speaker=em.sender_name,
                recipient=em.recipient_name,
                excerpt=em.body,
            )

            mentions.append(ActionMention(
                mention_id=f"email_{em.thread_id}_{em.email_index}",
                topic_key=topic,
                description=f"[{em.thread_subject}] {em.body}",
                owner=owner,
                counterparty=counterparty,
                claimed_deadline_str=claimed_str,
                claimed_deadline_date=d_date,
                claimed_deadline_time=d_time,
                evidence=evidence,
                status_indicator=status,
                is_unassigned_flag=is_unassigned,
            ))
        return mentions

    def extract_from_voice_notes(self, voice_notes: List[RawVoiceNote]) -> List[ActionMention]:
        mentions = []
        for vn in voice_notes:
            # Voice note 1 contains vendor list and mumbai lease
            # Voice note 2 contains expense variance report and meridian call
            text = vn.transcript

            # Split sentences/clauses for granular extraction
            clauses = re.split(r"\.\s+|\?\s+|!\s+", text)
            for c_idx, clause in enumerate(clauses):
                if not clause.strip():
                    continue
                topic = detect_topic(clause)
                if not topic:
                    continue

                is_unassigned = detect_unassigned(clause)
                claimed_str, d_date, d_time = parse_deadline_hints(clause, vn.timestamp.date())

                owner = None
                counterparty = None
                if topic == "vendor_list":
                    owner = "Arjun Malhotra"
                    counterparty = "Raghav Sethi"
                elif topic == "meridian_call":
                    owner = "Arjun Malhotra"
                    counterparty = "Priya Nair"
                elif topic == "expense_report":
                    owner = "Divya Rao"
                    counterparty = "Arjun Malhotra"
                elif topic == "mumbai_lease":
                    is_unassigned = True
                    owner = None

                evidence = EvidenceItem(
                    source_type=SourceType.VOICE_NOTE,
                    source_label=f"Voice Note {vn.note_id} ({vn.context})",
                    timestamp_str=vn.date_str,
                    timestamp=vn.timestamp,
                    sender_or_speaker="Arjun Malhotra (Self-memo)",
                    recipient=None,
                    excerpt=clause.strip(),
                )

                mentions.append(ActionMention(
                    mention_id=f"voicenote_{vn.note_id}_{c_idx+1}",
                    topic_key=topic,
                    description=clause.strip(),
                    owner=owner,
                    counterparty=counterparty,
                    claimed_deadline_str=claimed_str,
                    claimed_deadline_date=d_date,
                    claimed_deadline_time=d_time,
                    evidence=evidence,
                    status_indicator=ActionStatus.PENDING,
                    is_unassigned_flag=is_unassigned,
                ))
        return mentions

    def extract_all(self) -> List[ActionMention]:
        all_mentions = []
        for m in get_meeting_transcripts():
            all_mentions.extend(self.extract_from_meeting(m))
        all_mentions.extend(self.extract_from_emails(get_email_threads()))
        all_mentions.extend(self.extract_from_voice_notes(get_voice_notes()))
        return all_mentions
