"""AIONOS Assignment 1 Data Pack.

Contains the exact dataset provided for the Executive Action Copilot exercise
covering the week of Monday 21 September 2026 to Friday 25 September 2026.
Executive user: Arjun Malhotra (VP Sales).
"""
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import List, Dict, Any


@dataclass
class RawMeetingStatement:
    speaker: str
    text: str


@dataclass
class RawMeetingTranscript:
    meeting_title: str
    date_str: str
    meeting_date: date
    start_time: time
    end_time: time
    attendees: List[str]
    statements: List[RawMeetingStatement]


@dataclass
class RawCalendarEvent:
    person_name: str
    day_date_str: str
    event_date: date
    time_range_str: str
    event_title: str


@dataclass
class RawEmail:
    thread_id: int
    thread_subject: str
    email_index: int
    date_str: str
    timestamp: datetime
    sender_email: str
    sender_name: str
    recipient_email: str
    recipient_name: str
    body: str


@dataclass
class RawVoiceNote:
    note_id: int
    date_str: str
    timestamp: datetime
    context: str
    transcript: str


PEOPLE_DIRECTORY = {
    "arjun.malhotra@veridian-corp.example": {"name": "Arjun Malhotra", "role": "VP Sales (the agent's user)"},
    "neha.kapoor@veridian-corp.example": {"name": "Neha Kapoor", "role": "Marketing Lead"},
    "raghav.sethi@veridian-corp.example": {"name": "Raghav Sethi", "role": "Ops Manager"},
    "divya.rao@veridian-corp.example": {"name": "Divya Rao", "role": "Finance"},
    "priya.nair@meridianlogistics.example": {"name": "Priya Nair", "role": "Meridian Logistics (external client)"},
    "facilities@veridian-corp.example": {"name": "Facilities", "role": "Internal distribution list"},
}

NAME_TO_EMAIL = {v["name"]: k for k, v in PEOPLE_DIRECTORY.items()}


def get_meeting_transcripts() -> List[RawMeetingTranscript]:
    return [
        RawMeetingTranscript(
            meeting_title="Leadership Sync",
            date_str="Monday 21 September 2026, 9:00–9:35 AM",
            meeting_date=date(2026, 9, 21),
            start_time=time(9, 0),
            end_time=time(9, 35),
            attendees=["Arjun Malhotra", "Neha Kapoor", "Raghav Sethi", "Divya Rao"],
            statements=[
                RawMeetingStatement(
                    speaker="Arjun Malhotra",
                    text="Let's keep this quick. Neha, where are we on the Q3 campaign deck?"
                ),
                RawMeetingStatement(
                    speaker="Neha Kapoor",
                    text="Draft is 80% done. I'll send it to Arjun for review by Wednesday."
                ),
                RawMeetingStatement(
                    speaker="Arjun Malhotra",
                    text="Good. Also, remind me — I told Raghav I'd send him the updated vendor list. I'll get that to him by end of day tomorrow."
                ),
                RawMeetingStatement(
                    speaker="Raghav Sethi",
                    text="Appreciated. Separately, the Mumbai office renewal paperwork needs someone to sign off this week. Not sure whose desk that's on right now."
                ),
                RawMeetingStatement(
                    speaker="Divya Rao",
                    text="I think that's supposed to be Facilities, but I haven't seen anyone pick it up."
                ),
                RawMeetingStatement(
                    speaker="Arjun Malhotra",
                    text="Okay, flag it, don't assume. Divya, can you also pull the July expense variance report before Thursday's board prep?"
                ),
                RawMeetingStatement(
                    speaker="Divya Rao",
                    text="Yes, I'll have it ready Wednesday evening."
                ),
                RawMeetingStatement(
                    speaker="Arjun Malhotra",
                    text="One more thing — client call with Meridian Logistics got pushed. I need to reconfirm the new time with their team myself."
                ),
                RawMeetingStatement(
                    speaker="Neha Kapoor",
                    text="Also, just a reminder, the campaign deck review — I said Wednesday, but realistically Thursday morning is safer."
                ),
                RawMeetingStatement(
                    speaker="Arjun Malhotra",
                    text="Noted. Let's close here."
                ),
            ]
        )
    ]


def get_calendar_events() -> List[RawCalendarEvent]:
    events = [
        # Arjun Malhotra
        RawCalendarEvent("Arjun Malhotra", "Mon 21 Sep", date(2026, 9, 21), "9:00–9:35 AM", "Leadership Sync"),
        RawCalendarEvent("Arjun Malhotra", "Mon 21 Sep", date(2026, 9, 21), "2:00–2:30 PM", "1:1 with Neha"),
        RawCalendarEvent("Arjun Malhotra", "Mon 21 Sep", date(2026, 9, 21), "4:00–5:00 PM", "Blocked"),
        RawCalendarEvent("Arjun Malhotra", "Tue 22 Sep", date(2026, 9, 22), "11:00 AM–12:00 PM", "Internal Budget Review"),
        RawCalendarEvent("Arjun Malhotra", "Tue 22 Sep", date(2026, 9, 22), "3:00–3:30 PM", "Blocked"),
        RawCalendarEvent("Arjun Malhotra", "Wed 23 Sep", date(2026, 9, 23), "3:00–3:30 PM", "Call — Meridian Logistics"),
        RawCalendarEvent("Arjun Malhotra", "Wed 23 Sep", date(2026, 9, 23), "6:00–6:15 PM", "Blocked"),
        RawCalendarEvent("Arjun Malhotra", "Thu 24 Sep", date(2026, 9, 24), "9:00–10:00 AM", "Board Prep Session"),
        RawCalendarEvent("Arjun Malhotra", "Thu 24 Sep", date(2026, 9, 24), "4:00–5:00 PM", "Hiring Panel — Sales Associate"),
        RawCalendarEvent("Arjun Malhotra", "Fri 25 Sep", date(2026, 9, 25), "10:00–10:30 AM", "Facilities Check-in"),
        RawCalendarEvent("Arjun Malhotra", "Fri 25 Sep", date(2026, 9, 25), "1:00–2:00 PM", "Blocked"),

        # Neha Kapoor
        RawCalendarEvent("Neha Kapoor", "Mon 21 Sep", date(2026, 9, 21), "10:00–11:00 AM", "Blocked"),
        RawCalendarEvent("Neha Kapoor", "Mon 21 Sep", date(2026, 9, 21), "2:00–2:30 PM", "1:1 with Arjun"),
        RawCalendarEvent("Neha Kapoor", "Tue 22 Sep", date(2026, 9, 22), "1:00–2:00 PM", "Campaign Vendor Call"),
        RawCalendarEvent("Neha Kapoor", "Wed 23 Sep", date(2026, 9, 23), "10:00–10:30 AM", "Deck Prep"),
        RawCalendarEvent("Neha Kapoor", "Wed 23 Sep", date(2026, 9, 23), "1:00–3:00 PM", "Blocked"),
        RawCalendarEvent("Neha Kapoor", "Thu 24 Sep", date(2026, 9, 24), "9:30–10:00 AM", "Deck Review with Arjun"),
        RawCalendarEvent("Neha Kapoor", "Fri 25 Sep", date(2026, 9, 25), "11:00 AM–12:00 PM", "Blocked"),

        # Raghav Sethi
        RawCalendarEvent("Raghav Sethi", "Mon 21 Sep", date(2026, 9, 21), "9:00–9:35 AM", "Leadership Sync"),
        RawCalendarEvent("Raghav Sethi", "Mon 21 Sep", date(2026, 9, 21), "1:00–2:00 PM", "Blocked"),
        RawCalendarEvent("Raghav Sethi", "Tue 22 Sep", date(2026, 9, 22), "11:00 AM–12:00 PM", "Internal Budget Review"),
        RawCalendarEvent("Raghav Sethi", "Tue 22 Sep", date(2026, 9, 22), "3:30–4:00 PM", "Ops Standup"),
        RawCalendarEvent("Raghav Sethi", "Wed 23 Sep", date(2026, 9, 23), "9:00–11:00 AM", "Blocked"),
        RawCalendarEvent("Raghav Sethi", "Thu 24 Sep", date(2026, 9, 24), "2:00–3:00 PM", "Blocked"),
        RawCalendarEvent("Raghav Sethi", "Fri 25 Sep", date(2026, 9, 25), "10:00–10:30 AM", "Facilities Check-in"),
        RawCalendarEvent("Raghav Sethi", "Fri 25 Sep", date(2026, 9, 25), "3:00–4:00 PM", "Blocked"),

        # Divya Rao
        RawCalendarEvent("Divya Rao", "Mon 21 Sep", date(2026, 9, 21), "2:30–3:00 PM", "Budget Prep"),
        RawCalendarEvent("Divya Rao", "Mon 21 Sep", date(2026, 9, 21), "4:00–5:00 PM", "Blocked"),
        RawCalendarEvent("Divya Rao", "Tue 22 Sep", date(2026, 9, 22), "9:00–9:15 AM", "Quick Call with Arjun"),
        RawCalendarEvent("Divya Rao", "Tue 22 Sep", date(2026, 9, 22), "11:00 AM–12:00 PM", "Internal Budget Review"),
        RawCalendarEvent("Divya Rao", "Wed 23 Sep", date(2026, 9, 23), "1:00–2:00 PM", "Blocked"),
        RawCalendarEvent("Divya Rao", "Thu 24 Sep", date(2026, 9, 24), "9:00–10:00 AM", "Board Prep Session"),
        RawCalendarEvent("Divya Rao", "Thu 24 Sep", date(2026, 9, 24), "2:00–3:00 PM", "Blocked"),
        RawCalendarEvent("Divya Rao", "Fri 25 Sep", date(2026, 9, 25), "10:00–11:00 AM", "Blocked"),
    ]
    return events


def get_email_threads() -> List[RawEmail]:
    return [
        # Thread 1 — Subject: Vendor List
        RawEmail(
            thread_id=1,
            thread_subject="Vendor List",
            email_index=1,
            date_str="Mon 21 Sep, 9:50 AM",
            timestamp=datetime(2026, 9, 21, 9, 50),
            sender_email="raghav.sethi@veridian-corp.example",
            sender_name="Raghav Sethi",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Following up from the sync — can you send the updated vendor list today?"
        ),
        RawEmail(
            thread_id=1,
            thread_subject="Vendor List",
            email_index=2,
            date_str="Mon 21 Sep, 5:40 PM",
            timestamp=datetime(2026, 9, 21, 17, 40),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="raghav.sethi@veridian-corp.example",
            recipient_name="Raghav Sethi",
            body="Running behind, will send first thing tomorrow morning instead."
        ),
        RawEmail(
            thread_id=1,
            thread_subject="Vendor List",
            email_index=3,
            date_str="Tue 22 Sep, 9:15 AM",
            timestamp=datetime(2026, 9, 22, 9, 15),
            sender_email="raghav.sethi@veridian-corp.example",
            sender_name="Raghav Sethi",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="No worries, whenever you get a chance today works."
        ),
        RawEmail(
            thread_id=1,
            thread_subject="Vendor List",
            email_index=4,
            date_str="Tue 22 Sep, 6:30 PM",
            timestamp=datetime(2026, 9, 22, 18, 30),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="raghav.sethi@veridian-corp.example",
            recipient_name="Raghav Sethi",
            body="Sorry, got pulled into board prep — will send by tomorrow (Wednesday) morning for sure."
        ),
        RawEmail(
            thread_id=1,
            thread_subject="Vendor List",
            email_index=5,
            date_str="Wed 23 Sep, 8:45 AM",
            timestamp=datetime(2026, 9, 23, 8, 45),
            sender_email="raghav.sethi@veridian-corp.example",
            sender_name="Raghav Sethi",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Just checking — still good for this morning?"
        ),

        # Thread 2 — Subject: Q3 Campaign Deck
        RawEmail(
            thread_id=2,
            thread_subject="Q3 Campaign Deck",
            email_index=1,
            date_str="Mon 21 Sep, 11:00 AM",
            timestamp=datetime(2026, 9, 21, 11, 0),
            sender_email="neha.kapoor@veridian-corp.example",
            sender_name="Neha Kapoor",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Deck's coming together, still targeting Wednesday for your review."
        ),
        RawEmail(
            thread_id=2,
            thread_subject="Q3 Campaign Deck",
            email_index=2,
            date_str="Tue 22 Sep, 4:15 PM",
            timestamp=datetime(2026, 9, 22, 16, 15),
            sender_email="neha.kapoor@veridian-corp.example",
            sender_name="Neha Kapoor",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Heads up — shifting the review to Thursday morning instead of Wednesday, need one more day on the data slides."
        ),
        RawEmail(
            thread_id=2,
            thread_subject="Q3 Campaign Deck",
            email_index=3,
            date_str="Wed 23 Sep, 10:00 AM",
            timestamp=datetime(2026, 9, 23, 10, 0),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="neha.kapoor@veridian-corp.example",
            recipient_name="Neha Kapoor",
            body="Understood, Thursday morning works. What time exactly?"
        ),
        RawEmail(
            thread_id=2,
            thread_subject="Q3 Campaign Deck",
            email_index=4,
            date_str="Wed 23 Sep, 10:20 AM",
            timestamp=datetime(2026, 9, 23, 10, 20),
            sender_email="neha.kapoor@veridian-corp.example",
            sender_name="Neha Kapoor",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Let's say 9:30 AM Thursday, before your board prep block."
        ),
        RawEmail(
            thread_id=2,
            thread_subject="Q3 Campaign Deck",
            email_index=5,
            date_str="Thu 24 Sep, 8:00 AM",
            timestamp=datetime(2026, 9, 24, 8, 0),
            sender_email="neha.kapoor@veridian-corp.example",
            sender_name="Neha Kapoor",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Deck is ready, attaching the draft ahead of our 9:30 review."
        ),

        # Thread 3 — Subject: Call Reschedule
        RawEmail(
            thread_id=3,
            thread_subject="Call Reschedule",
            email_index=1,
            date_str="Mon 21 Sep, 1:00 PM",
            timestamp=datetime(2026, 9, 21, 13, 0),
            sender_email="priya.nair@meridianlogistics.example",
            sender_name="Priya Nair",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Our scheduled call this week got bumped from our side — can you propose a new time? We're flexible Tuesday–Thursday afternoons."
        ),
        RawEmail(
            thread_id=3,
            thread_subject="Call Reschedule",
            email_index=2,
            date_str="Tue 22 Sep, 3:00 PM",
            timestamp=datetime(2026, 9, 22, 15, 0),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="priya.nair@meridianlogistics.example",
            recipient_name="Priya Nair",
            body="Apologies for the delay — how about Wednesday 3:00 PM?"
        ),
        RawEmail(
            thread_id=3,
            thread_subject="Call Reschedule",
            email_index=3,
            date_str="Tue 22 Sep, 5:45 PM",
            timestamp=datetime(2026, 9, 22, 17, 45),
            sender_email="priya.nair@meridianlogistics.example",
            sender_name="Priya Nair",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Wednesday 3 PM works on our end, confirmed."
        ),
        RawEmail(
            thread_id=3,
            thread_subject="Call Reschedule",
            email_index=4,
            date_str="Wed 23 Sep, 1:30 PM",
            timestamp=datetime(2026, 9, 23, 13, 30),
            sender_email="priya.nair@meridianlogistics.example",
            sender_name="Priya Nair",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Quick check — still on for 3 PM today?"
        ),
        RawEmail(
            thread_id=3,
            thread_subject="Call Reschedule",
            email_index=5,
            date_str="Wed 23 Sep, 2:00 PM",
            timestamp=datetime(2026, 9, 23, 14, 0),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="priya.nair@meridianlogistics.example",
            recipient_name="Priya Nair",
            body="Yes, confirmed, see you at 3."
        ),

        # Thread 4 — Subject: Expense Variance Report
        RawEmail(
            thread_id=4,
            thread_subject="Expense Variance Report",
            email_index=1,
            date_str="Mon 21 Sep, 2:30 PM",
            timestamp=datetime(2026, 9, 21, 14, 30),
            sender_email="divya.rao@veridian-corp.example",
            sender_name="Divya Rao",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Starting on the July variance numbers, targeting Thursday morning for board prep as discussed."
        ),
        RawEmail(
            thread_id=4,
            thread_subject="Expense Variance Report",
            email_index=2,
            date_str="Tue 22 Sep, 9:00 AM",
            timestamp=datetime(2026, 9, 22, 9, 0),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="divya.rao@veridian-corp.example",
            recipient_name="Divya Rao",
            body="Actually, can I get it by Wednesday evening instead? Want time to review before Thursday."
        ),
        RawEmail(
            thread_id=4,
            thread_subject="Expense Variance Report",
            email_index=3,
            date_str="Tue 22 Sep, 9:40 AM",
            timestamp=datetime(2026, 9, 22, 9, 40),
            sender_email="divya.rao@veridian-corp.example",
            sender_name="Divya Rao",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Wednesday evening is tight but doable, I'll prioritize it."
        ),
        RawEmail(
            thread_id=4,
            thread_subject="Expense Variance Report",
            email_index=4,
            date_str="Wed 23 Sep, 6:00 PM",
            timestamp=datetime(2026, 9, 23, 18, 0),
            sender_email="divya.rao@veridian-corp.example",
            sender_name="Divya Rao",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="Report attached, sent as promised."
        ),
        RawEmail(
            thread_id=4,
            thread_subject="Expense Variance Report",
            email_index=5,
            date_str="Wed 23 Sep, 6:10 PM",
            timestamp=datetime(2026, 9, 23, 18, 10),
            sender_email="arjun.malhotra@veridian-corp.example",
            sender_name="Arjun Malhotra",
            recipient_email="divya.rao@veridian-corp.example",
            recipient_name="Divya Rao",
            body="Got it, thank you — exactly what I needed before tomorrow."
        ),

        # Thread 5 — Subject: Mumbai Office Lease Renewal
        RawEmail(
            thread_id=5,
            thread_subject="Mumbai Office Lease Renewal",
            email_index=1,
            date_str="Mon 21 Sep, 10:15 AM",
            timestamp=datetime(2026, 9, 21, 10, 15),
            sender_email="facilities@veridian-corp.example",
            sender_name="Facilities",
            recipient_email="all.staff@veridian-corp.example",
            recipient_name="All Staff",
            body="Reminder: the Mumbai office lease renewal requires an authorized signature by Friday, 25 September."
        ),
        RawEmail(
            thread_id=5,
            thread_subject="Mumbai Office Lease Renewal",
            email_index=2,
            date_str="Tue 22 Sep, 11:00 AM",
            timestamp=datetime(2026, 9, 22, 11, 0),
            sender_email="raghav.sethi@veridian-corp.example",
            sender_name="Raghav Sethi",
            recipient_email="arjun.malhotra@veridian-corp.example, divya.rao@veridian-corp.example",
            recipient_name="Arjun Malhotra, Divya Rao",
            body="Following up from the sync — has anyone confirmed who's signing off on the Mumbai renewal? Don't think it's been assigned."
        ),
        RawEmail(
            thread_id=5,
            thread_subject="Mumbai Office Lease Renewal",
            email_index=3,
            date_str="Wed 23 Sep, 9:30 AM",
            timestamp=datetime(2026, 9, 23, 9, 30),
            sender_email="divya.rao@veridian-corp.example",
            sender_name="Divya Rao",
            recipient_email="raghav.sethi@veridian-corp.example, arjun.malhotra@veridian-corp.example",
            recipient_name="Raghav Sethi, Arjun Malhotra",
            body="Not on my end — I believe this typically sits with Facilities directly, not us."
        ),
        RawEmail(
            thread_id=5,
            thread_subject="Mumbai Office Lease Renewal",
            email_index=4,
            date_str="Thu 24 Sep, 4:00 PM",
            timestamp=datetime(2026, 9, 24, 16, 0),
            sender_email="facilities@veridian-corp.example",
            sender_name="Facilities",
            recipient_email="all.staff@veridian-corp.example",
            recipient_name="All Staff",
            body="Second reminder: signature is still pending. Deadline is Friday, 25 September, end of day."
        ),
        RawEmail(
            thread_id=5,
            thread_subject="Mumbai Office Lease Renewal",
            email_index=5,
            date_str="Thu 24 Sep, 4:45 PM",
            timestamp=datetime(2026, 9, 24, 16, 45),
            sender_email="raghav.sethi@veridian-corp.example",
            sender_name="Raghav Sethi",
            recipient_email="arjun.malhotra@veridian-corp.example",
            recipient_name="Arjun Malhotra",
            body="This is now one day out and still unowned — can you confirm who's handling it?"
        ),
    ]


def get_voice_notes() -> List[RawVoiceNote]:
    return [
        RawVoiceNote(
            note_id=1,
            date_str="Monday 21 Sep, 6:40 PM",
            timestamp=datetime(2026, 9, 21, 18, 40),
            context="recorded in cab",
            transcript="Quick note to self — need to get Raghav that vendor list, I think I said today but it might slip to tomorrow morning, remind me. Also still haven't heard back on the Mumbai lease thing, someone needs to own that, I don't think it's me."
        ),
        RawVoiceNote(
            note_id=2,
            date_str="Wednesday 23 Sep, 8:15 AM",
            timestamp=datetime(2026, 9, 23, 8, 15),
            context="dictated memo",
            transcript="Reminder — expense variance report from Divya needs to be in my hands by Wednesday evening, not Thursday, I want time to go through it before board prep. Also Meridian call — I owe Priya a time, need to lock that in today."
        ),
    ]
