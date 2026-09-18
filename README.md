# AIONOS Assignment 1 — Executive Action Copilot MVP

A 100% local, zero-API, rule-based **Executive Action Copilot** designed for **Arjun Malhotra (VP Sales)**. The system ingests multi-source executive inputs (meeting transcripts, email threads, calendars, voice notes), extracts commitments and open items, deduplicates deliverables, chronologically reconciles deadlines and status, flags unclear ownership without guessing, compiles source evidence trails, generates daily briefs, and answers natural language queries.

---

## Architecture & Core Flow

```
[Raw Sources]
Meeting Transcripts  +  Email Threads  +  Calendars  +  Voice Memos
                         │
                         ▼
             1. EXTRACT (Rule-Based Parsing)
    Signals, Verbs of Commitment, Deliverables, Time Anchors
                         │
                         ▼
           2. DEDUPLICATE (Topic Clustering)
      Groups mentions into 5 canonical deliverable topics
                         │
                         ▼
       3. RECONCILE LATEST STATE (Chronological)
    Tracks deadline slips, completion acknowledgments, and state
                         │
                         ▼
     4. OWNERSHIP / DEADLINE / STATUS PARTITIONING
    • Ownership: My Actions | Waiting on Others | Unclear Ownership
    • Urgency:   Due Today | Overdue | Upcoming | Completed
                         │
                         ▼
         5. EVIDENCE CITATION COMPILATION
    Grounds every item with verbatim excerpts and audit timestamps
                         │
                         ▼
          6. DAILY BRIEF & HIGH-LEVEL LOGGING
    Executive Markdown Brief + Non-CoT Agent Activity Log
                         │
                         ▼
                   7. Q&A ENGINE
    Answers queries ("What did I promise Raghav?", "What needs action today?")
```

---

## Key Features & Constraints

- **Zero External AI / Zero Paid APIs**: Built entirely in Python standard library (`datetime`, `re`, `dataclasses`, `argparse`, `unittest`). No OpenAI, Claude, Gemini, vector DBs, ML models, or heavy frameworks.
- **Strict Grounding & Zero Guessing**: Unclear/unassigned items (such as the Mumbai office lease renewal) are strictly categorized as `Unclear Ownership` with zero invented owners.
- **Dynamic Chronological Reconciliation**: Tracks commitments evolving across the week (e.g., vendor list slipping from Tuesday EOD to Tuesday morning to Wednesday morning; campaign deck shifting to Thursday 9:30 AM).
- **Audit-Grade Evidence Trail**: Every deliverable, status, and Q&A response is directly backed by timestamps, speakers, recipients, and exact quotations.
- **High-Level Agent Activity**: Clean agent activity steps logged (`INGEST`, `EXTRACT`, `DEDUPLICATE`, `RECONCILE`, `CLASSIFY`, `BRIEF_READY`, `Q&A`) without internal chain-of-thought rambling.

---

## Deliverables & Reconciled States (Week of 21–25 Sep 2026)

| # | Deliverable Topic | Owner | Category | Reconciled Deadline | Status (as of Fri 25 Sep) |
|---|---|---|---|---|---|
| 1 | **Send updated vendor list to Raghav Sethi** | Arjun Malhotra | **My Actions** | Wednesday 23 Sep, Morning (9:00 AM) | **Overdue** (Slipped twice, unfulfilled) |
| 2 | **Review Q3 Campaign Deck with Neha Kapoor** | Arjun Malhotra | **My Actions** | Thursday 24 Sep, 9:30 AM | **Completed** (Deck received Thu 8:00 AM, reviewed) |
| 3 | **Meridian Logistics Client Call (Priya Nair)** | Arjun Malhotra | **My Actions** | Wednesday 23 Sep, 3:00 PM | **Completed** (Confirmed and held) |
| 4 | **July Expense Variance Report (Divya Rao)** | Divya Rao | **Waiting on Others** | Wednesday 23 Sep, 6:00 PM | **Completed** (Delivered Wed 6:00 PM) |
| 5 | **Mumbai Office Lease Renewal Sign-off** | *Unassigned* | **Unclear Ownership** | Friday 25 Sep, End of Day (5:00 PM) | **Due Today / Urgent** (Still unowned!) |

---

## Quick Start & Usage

### 1. Interactive Web Dashboard (Localhost)
Start the local web server:
```bash
python server.py 8000
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

The Web Dashboard features:
- **Date Switcher tabs** (Mon 21 Sep to Fri 25 Sep) with dynamic state transitions.
- **Agent Activity Log strip** showing live pipeline execution.
- **Categorized 3-Column Matrix** (My Actions, Waiting on Others, Unclear Ownership).
- **Collapsible Source Citations** on every action item.
- **Interactive Q&A Console** with quick-prompt chips and instant grounded answers.
- **Daily Calendar Schedule** for Arjun Malhotra.

### 2. Run Default Daily Brief (CLI)
```bash
python main.py
```

### 2. View Daily Brief for Another Date (e.g., Wednesday 23 Sep 2026)
```bash
python main.py --date 2026-09-23
```
*Notice how Vendor List, Meridian Call, and Expense Report show as **Due Today**, Campaign Deck is **Upcoming**, and Mumbai Lease is **Upcoming**.*

### 3. Ask Questions (CLI Q&A)
```bash
# What did I promise Raghav?
python main.py --ask "What did I promise Raghav?"

# What needs action today?
python main.py --ask "What needs action today?"

# What items have unclear ownership?
python main.py --ask "What items have unclear ownership?"

# Did Divya send the expense report?
python main.py --ask "Did Divya send the expense report?"

# What is overdue?
python main.py --ask "What is overdue?"
```

### 4. Interactive Q&A Mode
```bash
python main.py --interactive
```
Type questions interactively or enter `brief`, `my actions`, or `quit`.

### 5. Run Automated Verification Test Suite
```bash
python -m unittest test_copilot.py -v
```

---

## Project Structure

```
.
├── data_pack.py         # Raw source data structures and ingested AIONOS dataset
├── models.py            # Enums and dataclasses (ActionMention, ReconciledAction, DailyBrief, etc.)
├── extractor.py         # Rule-based action mention, deadline, and ownership parser
├── deduplicator.py      # Semantic topic clustering and deduplication
├── reconciler.py        # Chronological progression, deadline resolution, and urgency engine
├── brief_generator.py   # Daily Action Brief generator with Agent Activity logging
├── qa_engine.py         # Grounded question-answering engine with evidence citations
├── copilot.py           # Core orchestrator tying pipeline together
├── main.py              # CLI and interactive shell
├── test_copilot.py      # 10 comprehensive unit tests
└── README.md            # System documentation and execution guide
```
