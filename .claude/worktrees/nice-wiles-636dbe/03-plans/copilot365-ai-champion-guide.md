# Copilot 365 AI Champion — R&D Division
## Hands-On Implementation Guide for POC & Presentation

**Author:** AI Champion, R&D Division
**Date:** April 2026
**Audience:** Management + R&D Colleagues (10 people)
**License:** Microsoft Copilot for Microsoft 365 (broadly assigned)
**Goal:** Demonstrate 11 working use cases, hands-on, in a 2-week POC sprint

---

## How to Use This Document

Each use case below contains:
- **What it does** — plain language description
- **Why it matters** — the business value (use this language with management)
- **Step-by-step implementation** — exact clicks and configurations to build the POC yourself
- **Demo script** — what to say and show during the presentation
- **Effort estimate** — realistic time to build the POC

Work through them in order — Use Cases 1 and 5 are the fastest wins.

**Use Case Index**

| # | Title | Tool | POC Effort |
|---|-------|------|------------|
| 1 | Project Knowledge Agent | Copilot Studio + SharePoint | ~75 min |
| 2 | Jira Natural Language Query | Power Automate + REST API | ~110 min |
| 3 | Excel Planning Analysis | Copilot in Excel | ~60 min |
| 4 | Excel → PowerPoint Pipeline | Word + PowerPoint Copilot | ~40 min |
| 5 | Outlook Email Management | Rules + Outlook Copilot | ~60 min |
| 6 | Teams Meeting Intelligence | Teams Copilot + Recap | ~25 min |
| 7 | Word Technical Documentation | Copilot in Word | ~35 min |
| 8 | Power Automate R&D Flows | Copilot in Power Automate | ~90 min |
| 9 | Copilot Researcher (Deep Research) | M365 Copilot Researcher Agent | ~30 min |
| 10 | Microsoft Loop for R&D Collaboration | Copilot in Loop | ~30 min |
| 11 | Copilot Analyst — Data Insights | M365 Copilot Analyst Agent | ~30 min |

---

## Use Case 1 — Project Knowledge Agent (SharePoint RAG)

### What it does
A conversational agent that knows everything about a project — specs, decisions, architecture docs, meeting notes, reference files — all stored in SharePoint. Team members ask it questions in natural language instead of searching through folders.

### Why it matters
> "Instead of spending 15 minutes searching through 40 documents, anyone on the team gets the answer in 10 seconds with a source link. Onboarding new team members goes from days to hours."

### Prerequisites
- Copilot Studio access (included in Copilot M365 license)
- A SharePoint document library with at least one project's documents
- No admin rights needed for a personal POC

### Step-by-Step Implementation

#### Step 1 — Prepare your SharePoint library (15 min)
1. Go to your SharePoint site → **Documents**
2. Create a folder named `Enigma-Knowledge` (or your project name)
3. Upload a representative set of documents:
   - Project charter or scope document
   - Architecture decision records
   - Meeting notes (last 3-5 meetings)
   - Technical specifications
   - FAQ or known issues log
4. Make sure the library is shared with your team (not just you)

> **Tip:** The more structured and well-named your documents, the better the agent's answers. Rename files descriptively: `2025-Q1-Architecture-Decision-AuthModule.docx` beats `doc_v3_final.docx`

#### Step 2 — Create the Copilot Studio agent (30 min)
1. Go to [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) — sign in with your M365 account
2. Click **+ Create** → **New agent**
3. Name it: `Enigma Project Assistant` (or your project name)
4. In the description field, write:
   > "I am the knowledge assistant for Project Enigma. I answer questions about project scope, architecture decisions, specifications, and status based on official project documents."
5. Click **Create**

#### Step 3 — Connect SharePoint as knowledge source (10 min)
1. Inside your agent, go to **Knowledge** tab (left sidebar)
2. Click **+ Add knowledge** → **SharePoint**
3. Paste your SharePoint site URL and select the `Enigma-Knowledge` folder
4. Click **Add** — indexing takes 5-10 minutes
5. Set **Search behavior**: "Always search knowledge first"

#### Step 4 — Configure agent instructions (10 min)
In the **Instructions** field, paste:

```
You are the Project Enigma knowledge assistant for the R&D team at Cognyte.

Always:
- Answer based on documents in your knowledge base
- Cite the source document name in your answer
- If the answer is not in your knowledge base, say "I don't have that information in the project documents — try asking [team member name] or checking [location]"
- Keep answers concise (3-5 bullets for complex topics, 1-2 sentences for simple ones)

Never:
- Make up information not in the documents
- Answer questions outside the scope of Project Enigma
```

#### Step 5 — Test before publishing (15 min)
In the **Test** panel on the right, try these questions:
- *"What is the scope of Project Enigma?"*
- *"What was decided about the authentication approach?"*
- *"What are the known risks?"*
- *"Summarize the latest meeting notes"*

Check that answers cite sources. Refine instructions if needed.

#### Step 6 — Publish to Teams (5 min)
1. Click **Publish** → **Microsoft Teams**
2. Choose **Share with my organization** (or just your team for POC)
3. The agent appears as a bot in Teams — your colleagues can chat with it directly

### Demo Script
> "Let me show you something. I'm going to ask our project agent a question that would normally require me to open 3 different documents."
>
> *[Type in Teams chat]: "What integration approach did we decide for the HLP module and why?"*
>
> *[Agent responds with the decision, the rationale, and cites the document]*
>
> "The agent read that from our architecture decision record. This is available to everyone on the team, 24/7, in any language."

### Effort Estimate
| Task | Time |
|------|------|
| Prepare SharePoint folder | 15 min |
| Create agent in Copilot Studio | 30 min |
| Connect knowledge + test | 25 min |
| Publish to Teams | 5 min |
| **Total** | **~75 min** |

---

## Use Case 2 — Jira in Plain Language (On-Prem Workaround)

### What it does
A Power Automate flow that accepts natural language input (typed in Teams or Outlook), calls the Jira REST API, and returns results — no JQL required. Team members query their backlog like a conversation.

### Why it matters
> "JQL is a barrier. Non-technical team members can't use it, and even engineers waste time remembering syntax. This replaces JQL with plain English for the 90% of queries we run every day."

### Prerequisites
- Power Automate license (included in M365)
- Jira on-prem REST API accessible from your network (confirm with IT)
- A Jira service account with API token (or basic auth) — request from your admin
- Basic knowledge of your Jira project key (e.g., `HLP`, `ENG`)

### Architecture Overview
```
User types in Teams/Outlook
        ↓
Power Automate flow triggered
        ↓
Copilot parses intent → maps to Jira REST parameters
        ↓
HTTP call to Jira REST API (/rest/api/2/search)
        ↓
Results formatted and returned to user
```

### Step-by-Step Implementation

#### Step 1 — Verify Jira REST API access (15 min)
From your browser, test this URL (replace with your Jira instance):
```
https://your-jira-instance/rest/api/2/myself
```
You should see a JSON response with your user info. If not, contact IT to ensure API access is open.

#### Step 2 — Create the Power Automate flow (45 min)

1. Go to [https://make.powerautomate.com](https://make.powerautomate.com)
2. Click **+ Create** → **Instant cloud flow**
3. Name it: `Jira Natural Language Query`
4. Trigger: **Manually trigger a flow**
5. Add an input: **Text** — label it `User Query`

**Add these steps:**

**Step A — Parse query intent with Copilot**
- Add action: **AI Builder** → **Extract information from text with a prompt**
- Prompt:
  ```
  Given this user request: "@{triggerBody()['text']}"

  Extract these fields as JSON:
  - assignee: the person mentioned (or "currentUser" if "me"/"my" is used)
  - priority: High/Medium/Low/any (default: "any")
  - status: Open/In Progress/Done/any (default: "Open")
  - project: project key if mentioned (default: "HLP")
  - sprint: "current" or "all" (default: "current")
  - type: Bug/Story/Task/any (default: "any")

  Return only valid JSON. No explanation.
  ```

**Step B — Build the JQL string**
- Add action: **Initialize variable** → `JQL_Query` (string)
- Value expression:
  ```
  concat('project = HLP AND status = "', outputs('AI_Builder')?['priority'], '"')
  ```
  *(Adjust based on your actual JSON parsing — this is simplified)*

**Step C — Call Jira REST API**
- Add action: **HTTP**
- Method: `GET`
- URI: `https://your-jira-instance/rest/api/2/search?jql=@{variables('JQL_Query')}&maxResults=10&fields=summary,status,assignee,priority`
- Headers:
  - `Authorization`: `Basic [base64(username:api_token)]`
  - `Content-Type`: `application/json`

**Step D — Format and return results**
- Add action: **Create HTML table** from the issues array
- Or use **Compose** to build a plain text summary for Teams

#### Step 3 — Create a Teams bot trigger (optional, 20 min)
Instead of running manually, connect this flow to a Teams message:
1. Change trigger to: **When a keyword is mentioned** in Teams
2. Keyword: `@JiraBot` or `/jira`
3. When a team member types `/jira show me my open bugs from this sprint`, the flow runs automatically

#### Step 4 — Test queries
Try these natural language inputs:
- `"Show me all open bugs assigned to me in the current sprint"`
- `"What high priority stories are blocked?"`
- `"How many tasks are in progress for the HLP project?"`

### Demo Script
> "Today if you want to query Jira, you need to write JQL. Watch what happens when I replace that with plain English."
>
> *[Type in Teams]: `/jira show me all high priority bugs assigned to me in the current sprint`*
>
> *[Flow runs, returns formatted list of issues]*
>
> "No JQL. No Jira login. The answer comes directly into Teams. This works for anyone on the team, technical or not."

### Effort Estimate
| Task | Time |
|------|------|
| Verify API + get credentials | 15 min |
| Build Power Automate flow | 45 min |
| Test and tune parsing | 30 min |
| Connect to Teams trigger | 20 min |
| **Total** | **~110 min** |

---

## Use Case 3 — Excel Planning Analysis with Copilot

### What it does
Using Copilot inside Excel to analyze your block-based project timeline, answer scheduling questions in natural language, identify delays, gaps, and risks — without building any formulas or pivot tables.

### Why it matters
> "Our planning tool is Excel. It works. We're not replacing it. But now we can ask it questions like 'which workstream is behind?' and get an instant answer instead of manually scanning every row."

### Understanding Your File Structure (Strategy_HLP-1703.xlsx)

Based on your description, your Excel file follows this pattern:
```
Row 1:   [Label]  | W1 | W2 | W3 | ... | W52   ← Time axis (weeks or months)
Row 2:   Timeline | [milestone blocks]          ← Key dates & milestones
Row 3:   Platform | [lab/env availability]      ← Infrastructure schedule
Row 4+:  [Team/Discipline] | [work blocks]      ← Team assignments
```
Each "block" = contiguous filled/labeled cells across the time axis = a scheduled work period.

### Step-by-Step Implementation

#### Step 1 — Prepare the Excel file for Copilot (10 min)
Copilot in Excel works best when:
1. Your data has a proper header row with clear labels
2. Column A contains lane names (Timeline, Platform, SW, HW, etc.)
3. Blocks have text labels, not just colors (add short text like "Design", "Dev", "Test" inside colored cells)
4. The file is saved to **OneDrive or SharePoint** (not just local Desktop)

> **Action:** Save a copy of `Strategy_HLP-1703.xlsx` to your SharePoint project folder.

#### Step 2 — Enable Copilot in Excel (2 min)
1. Open the file from SharePoint/OneDrive in Excel (desktop app)
2. Click the **Copilot** button in the Home ribbon (right side)
3. The Copilot panel opens on the right

#### Step 3 — Ask planning questions (ongoing)
Type these prompts in the Copilot panel:

**Status overview:**
> "Summarize the current status of each workstream. Which ones are on schedule and which are delayed?"

**Milestone awareness:**
> "List all milestones and their planned dates. Which milestones are coming up in the next 4 weeks?"

**Risk identification:**
> "Are there any gaps in the schedule where no work is assigned? List them by workstream."

**Resource conflicts:**
> "Are there any periods where more than 2 workstreams are active simultaneously? When are they?"

**Management summary:**
> "Write a 5-bullet executive summary of the project schedule suitable for a status report."

#### Step 4 — Generate a management summary table (10 min)
Ask Copilot:
> "Create a new sheet called 'Summary' with a table showing: Workstream | Planned Start | Planned End | Status | Notes. Fill it in based on the data in this file."

Copilot will generate the table. Review and correct any misreads.

### Demo Script
> "This is our standard planning file — the same Excel we've been using for years. I'm not changing the format. I'm adding a conversation to it."
>
> *[Open file, open Copilot panel]*
>
> *[Type]: "Which workstream has the longest delay compared to its original plan?"*
>
> *[Copilot responds with analysis]*
>
> "I used to spend 20 minutes answering that question in a status meeting. Now it takes 5 seconds."

### Effort Estimate
| Task | Time |
|------|------|
| Save file to SharePoint, add text labels to blocks | 20 min |
| Test key prompts and tune | 30 min |
| Generate summary sheet | 10 min |
| **Total** | **~60 min** |

---

## Use Case 4 — Excel Planning → PowerPoint Auto-Generation

### What it does
Using the summary generated in Use Case 3 as input, Copilot in PowerPoint automatically builds a management-ready status presentation — timeline slide, workstream status, risks, next steps.

### Why it matters
> "Every sprint review I spend 2 hours reformatting the Excel data into slides. This generates the first draft in under 2 minutes. I spend my time on content, not formatting."

### Step-by-Step Implementation

#### Step 1 — Prepare the input document (15 min)
The cleanest path to PowerPoint generation is through Word:

1. Open **Word** (new blank document)
2. Ask Copilot in Word to draft the content:
   > "Write a project status update for Project Enigma based on the following: [paste the 5-bullet summary from Excel Copilot]. Include: current status, key milestones, risks, and next steps."
3. Review and edit the Word doc
4. Save it to SharePoint: `Enigma-Status-Input.docx`

#### Step 2 — Generate the PowerPoint (10 min)
1. Open **PowerPoint** → blank presentation
2. Click **Copilot** in the Home ribbon
3. Click **Create presentation from file**
4. Select `Enigma-Status-Input.docx` from SharePoint
5. Copilot generates a full deck in ~30 seconds

#### Step 3 — Refine the generated deck (20 min)
Ask Copilot inside PowerPoint to improve specific slides:

- *"Make slide 2 more visual — replace the bullet list with an icon-based layout"*
- *"Add a timeline slide showing Q1 to Q3 milestones"*
- *"Change the color theme to match our corporate brand"*
- *"Add a risks slide with a red/amber/green status table"*

#### Step 4 — Direct Excel → PowerPoint (alternative)
If you prefer to skip Word:
1. In PowerPoint Copilot, type:
   > "Create a project status presentation. The project is called Enigma HLP-1703. It covers [paste key dates and workstreams directly]. Include an executive summary, schedule overview, team allocation, and top 3 risks."
2. Attach the Excel file when Copilot asks for supporting data

### Recommended Slide Structure (POC deck)
```
Slide 1: Title — Project Enigma | Status Update | [Date]
Slide 2: Executive Summary (5 bullets)
Slide 3: Schedule Overview (visual timeline)
Slide 4: Workstream Status (RAG table: Red/Amber/Green)
Slide 5: Team Allocation (who is doing what, when)
Slide 6: Top Risks & Mitigations
Slide 7: Next Milestones (next 4 weeks)
Slide 8: Decisions Needed (action items for management)
```

### Demo Script
> "I have my Excel planning file. I have a Word summary. Watch how long it takes to go from those two files to a management deck."
>
> *[Open PowerPoint → Copilot → Create from file → select Word doc]*
>
> *[30 seconds later, 8-slide deck appears]*
>
> "First draft in 30 seconds. I'll spend 15 minutes refining it instead of 2 hours building it from scratch."

### Effort Estimate
| Task | Time |
|------|------|
| Prepare Word input doc | 15 min |
| Generate PowerPoint | 5 min |
| Refine slides with Copilot prompts | 20 min |
| **Total** | **~40 min** |

---

## Use Case 5 — Outlook Email Management: Rules + Copilot + Daily Rhythm

> 📄 **Full hands-on guide:** `03-plans/outlook-copilot-daily-efficiency.md`
> This section summarizes the system. For click-by-click setup instructions, Power Automate flow templates, agent build steps, and the complete prompt card — open the dedicated guide above.

### What it does
A full daily email efficiency system combining Copilot inbox prioritization, smart rules, automated morning briefing, end-of-day report, and task extraction — so high email volume stops consuming your attention throughout the day.

### Why it matters
> "I get 80+ emails per day across 3 projects. The goal is not to process fewer emails — it's to stop email from interrupting deep work. Copilot + automation does the triage. I check in twice a day and everything else runs itself."

### Your New Daily Email Rhythm (the system in one view)
```
07:30 AM  Scheduled Copilot prompt → morning briefing in Teams/email
          What needs attention + today's meetings + overdue tasks

DURING DAY Rules + Copilot prioritization run silently
          High-priority surfaces. Jira/system noise routed away.

05:00 PM  Power Automate flow → End-of-Day Report to your inbox
          Flagged emails + tasks created + unanswered threads
```

### Part A — Smart Rules Setup (30 min total)

#### Rule Set 1: Project-Based Sorting
Create one rule per active project:

1. **Settings** → **Mail** → **Rules** → **+ Add new rule**
2. **Rule: Project Enigma**
   - Condition: Subject contains `HLP` OR `Enigma`
   - Action: Move to folder `Projects/Enigma`
   - Exception: From [your manager] → keep in Inbox

3. **Rule: Jira Notifications**
   - Condition: From contains `jira` OR `@your-jira-domain`
   - Action: Move to folder `Tools/Jira-Alerts`
   - Mark as read automatically (to clear badge count)

4. **Rule: CI/CD & System Alerts**
   - Condition: From contains `noreply` OR `jenkins` OR `gitlab`
   - Action: Move to folder `Tools/System-Alerts`
   - Mark as read automatically

5. **Rule: CC'd emails (not direct)**
   - Condition: My name is in the CC field (not To)
   - Action: Move to folder `FYI`
   - Note: Review this folder twice a day, not continuously

6. **Rule: Priority Flag — Manager**
   - Condition: From = [your manager's email]
   - Action: Flag as important + play notification sound
   - (Overrides Focused Inbox sorting)

#### Rule Set 2: Time-of-Day Priority Processing
- Set a **Daily review routine**: Check `FYI` and `Tools/Jira-Alerts` at 9am and 4pm only
- Keep **Inbox** only for emails that are addressed directly to you and not caught by rules
- **Focused Inbox** handles the rest automatically

### Part B — Copilot Features in Outlook (daily use)

#### Feature 1: Thread Summarization
**When to use:** Any thread with 5+ replies before you read it.

1. Open the email thread
2. Click **Copilot** button at top of the reading pane
3. Click **Summary by Copilot**
4. Copilot shows: key decisions, open questions, action items
5. Ask follow-up: *"What do I need to respond to?"*

#### Feature 2: Copilot-Assisted Reply
**When to use:** Emails that need a thoughtful reply but not a long one.

1. Click **Reply**
2. In the compose area, click **Copilot** → **Draft with Copilot**
3. Describe what you want:
   - *"Decline politely and suggest rescheduling to next week"*
   - *"Ask for the status update by Friday, keep it under 3 sentences"*
   - *"Agree and confirm I'll prepare the slides by Thursday"*
4. Copilot drafts — you review and send

#### Feature 3: Coaching (tone & clarity)
**When to use:** Important emails to management or external stakeholders.

1. Draft your email
2. Click **Copilot** → **Coaching by Copilot**
3. Copilot scores: Tone, Clarity, Reader sentiment, Length
4. Apply suggested improvements

#### Feature 4: Meeting Prep from Email
**When to use:** Before a meeting — get context from related emails.

1. Open a meeting invite in Outlook
2. Click **Copilot** → *"What do I need to know before this meeting?"*
3. Copilot searches your email and calendar for related context
4. Returns: last discussion on the topic, open items, attendee context

### Part C — Folder Structure Template
```
Inbox (direct emails to you only)
├── Projects/
│   ├── Enigma/
│   ├── [Project 2]/
│   └── [Project 3]/
├── Tools/
│   ├── Jira-Alerts/
│   ├── Confluence/
│   └── System-Alerts/
├── FYI/          ← CC'd emails
├── Archive/      ← processed, not needed
└── Action-Required/  ← manually flagged for follow-up
```

### Key Features Summary

| Feature | Where | What it does |
|---------|-------|-------------|
| Inbox prioritization | Outlook Settings → Copilot | Auto-scores every email: High/Normal/Low |
| Thread summarization | Copilot button in reading pane | Key points, decisions, open questions, action items |
| Attachment summary | Hover over PDF/Word/PPT attachment | Summarizes document without opening it |
| Draft with Copilot | Compose → Copilot | Generates reply from your one-line instruction |
| Email coaching | Compose → Coaching by Copilot | Scores tone, clarity, reader sentiment |
| Natural language search | Search bar → plain English | Finds emails by context, not just keywords |
| Smart scheduling | Copilot → Schedule meeting | Reads thread, creates invite, finds available time |
| Scheduled briefing | copilot.microsoft.com → Schedule | Auto-generates morning and evening reports |
| EOD digest flow | Power Automate | Sends daily summary of flagged/unread + tasks |
| Flag → Task flow | Power Automate | Auto-creates To Do task when you flag an email |
| Focus time booking | Teams → Viva Insights | Blocks 2-4 hrs/day for deep work automatically |
| Email Assistant agent | Copilot Studio | Conversational agent: triage, draft, organize |

### Demo Script
> "I get 80+ emails a day. Let me show you 4 things that changed how I work."
>
> *[1 — Show the 7:30 AM briefing output in Teams/email]*
> "This is what I read instead of opening my inbox at 7:30. I know my priorities before the day starts."
>
> *[2 — Open a 15-email thread → Copilot summary]*
> "15 messages. 10 seconds. One task created. Done."
>
> *[3 — Show End-of-Day Report email from Power Automate]*
> "Every day at 5pm this arrives automatically. I know exactly what I didn't get to."
>
> *[4 — Natural language search for something specific]*
> "Instead of remembering which folder it's in, I just describe it."

### Effort Estimate
| Task | Time |
|------|------|
| Create folder structure | 10 min |
| Configure 8 inbox rules | 20 min |
| Enable Copilot inbox prioritization | 5 min |
| Set up morning briefing scheduled prompt | 15 min |
| Build End-of-Day Report (Power Automate) | 35 min |
| Build Flag → To Do task flow | 20 min |
| Enable Viva Insights focus time | 10 min |
| **Total** | **~115 min** |
| **For POC demo only (rules + briefing + EOD flow)** | **~60 min** |

---

## Use Case 6 — Teams Meeting Intelligence

### What it does
Copilot in Teams automatically transcribes meetings, generates summaries, extracts action items, and answers questions about what was discussed — even if you join late or miss the meeting entirely.

### Why it matters
> "How many times has a decision been made in a meeting and three people walk away with three different understandings? Copilot creates a single source of truth for every meeting."

### Prerequisites
- Teams Premium license OR Copilot M365 (included)
- Meeting recording must be enabled for your tenant (verify with IT)
- Attendees should be informed that recording/transcription is active (compliance)

### Step-by-Step Implementation

#### Step 1 — Enable transcription in a meeting
1. Join or start a Teams meeting
2. Click **More** (⋯) → **Record and transcribe** → **Start transcription**
3. All attendees see a notification that transcription is running
4. Talk normally — Copilot transcribes in real time

#### Step 2 — Use Copilot during the meeting
In the meeting window, click the **Copilot** icon (right panel):

- *"Summarize the discussion so far"* — useful when you join late
- *"What are the open questions?"*
- *"List the decisions made"*
- *"What action items have been assigned?"*

#### Step 3 — Use Copilot after the meeting
1. In Teams, go to **Chat** → find the meeting → click **Recap**
2. Copilot has generated:
   - Full transcript (searchable)
   - AI summary (3-5 paragraphs)
   - Action items with assignees
   - Chapter markers by topic

Ask follow-up questions:
- *"What did [person] say about the timeline?"*
- *"Was there a decision on the authentication approach?"*
- *"Draft follow-up email with the action items from this meeting"*

#### Step 4 — Share the recap
1. From the meeting recap, click **Share**
2. Send recap to Teams channel or email thread
3. Everyone has the same understanding — no "I thought we decided..."

### Demo Script
> "Yesterday I had a 90-minute technical review. Instead of taking manual notes, I let Copilot transcribe. After the meeting, here's the recap."
>
> *[Open Teams meeting recap → show summary, action items]*
>
> *[Ask]: "Was there a decision on the integration approach?"*
>
> *[Copilot quotes the exact moment with speaker and timestamp]*
>
> "Every decision is now documented, searchable, and attributed. This eliminates a whole category of misunderstandings."

### Effort Estimate
| Task | Time |
|------|------|
| Enable transcription + test in one meeting | 10 min |
| Explore recap features post-meeting | 15 min |
| **Total** | **~25 min** |

---

## Use Case 7 — Copilot in Word: Technical Documentation from Bullets

### What it does
Convert rough notes, bullet points, or a verbal description into a structured technical document — PRD, architecture decision record, test plan, or meeting minutes — using Copilot in Word.

### Why it matters
> "Writing documentation is a tax on engineering time. We know what needs to be written — we just don't have time to format and structure it. Copilot turns a 10-minute brain dump into a first-draft document."

### Step-by-Step Implementation

#### Step 1 — Prepare your bullet notes
Open Notepad or Word and write rough bullets — do not worry about formatting:
```
- HLP module needs new auth
- decision: use OAuth2 with Cognyte SSO
- reasons: compliance req, reduce password fatigue, IT asked for it
- owner: [name]
- open: do we need 2FA for lab machines?
- timeline: must be done before Q3 FAT
```

#### Step 2 — Generate the document with Copilot
1. Open a new Word document (must be saved to OneDrive/SharePoint)
2. Click **Copilot** in the Home ribbon → **Draft with Copilot**
3. Type:
   > "Write an Architecture Decision Record for the following decision: [paste your bullets]. Use sections: Context, Decision, Reasoning, Consequences, Open Questions, Owner, Timeline."
4. Copilot generates the full document in seconds

#### Step 3 — Iterate with follow-up prompts
- *"Make the reasoning section more formal and technical"*
- *"Add a risks section with 3 potential risks of this decision"*
- *"Shorten the consequences section to 3 bullet points"*
- *"Add a table at the top with: Decision | Owner | Status | Date"*

#### Step 4 — Use templates for repeatability
Create one good document (ADR, meeting minutes, PRD), save it as a Word template:
1. **File** → **Save As** → **Word Template (.dotx)**
2. Save to your SharePoint templates folder
3. Next time: **New from template** → Copilot fills it in

### Use Case Variants
| Document Type | Prompt Starter |
|---------------|---------------|
| Architecture Decision Record | "Write an ADR for the following decision..." |
| Meeting Minutes | "Write formal meeting minutes from these notes..." |
| Test Plan | "Write a test plan for [feature] covering these scenarios..." |
| Risk Register | "Create a risk register table from these concerns..." |
| Status Report | "Write a weekly status report from these bullet points..." |

### Effort Estimate
| Task | Time |
|------|------|
| Prepare bullet notes | 5 min |
| Generate and refine first document | 20 min |
| Save as reusable template | 10 min |
| **Total** | **~35 min** |

---

---

## Use Case 8 — Power Automate (Flow) R&D Workflows with Copilot

### What it does
Power Automate — previously known as Microsoft Flow — is the M365 automation engine. In 2025-2026, Copilot is built directly into Power Automate: you describe what you want automated in plain English, and Copilot builds the flow, sets up connections, configures logic, and even helps debug when something breaks. No coding required.

### Why it matters
> "Every week I manually do things that could run automatically: notifications when a document is updated, weekly status digests, approval requests, Jira syncs. Each of these is 5-10 minutes of manual work. Automating them frees up hours per week — and they never get forgotten."

### Prerequisites
- Power Automate is included in your M365 license (go to [make.powerautomate.com](https://make.powerautomate.com))
- Copilot in Power Automate is enabled for Copilot M365 users — no extra setup
- For Jira on-prem flows: confirm REST API is accessible from your network (same as Use Case 2)

### How Copilot in Power Automate Works

Instead of building a flow step-by-step, you describe it:

1. Go to [make.powerautomate.com](https://make.powerautomate.com)
2. Click **+ Create** → **Describe it to design it** (Copilot mode)
3. Type your automation in plain language
4. Copilot proposes a full flow — triggers, actions, conditions, connections
5. Review, adjust parameters, save and test

You can then refine in conversation:
> "Add a condition: only run this if the file is a PDF"
> "Send the notification to Teams instead of email"
> "Add an approval step before the final action"

### 4 R&D Flows to Build for the POC

---

#### Flow A — Document Ready Notification (20 min to build)

**Scenario:** When a new document is uploaded to the Enigma SharePoint folder, automatically notify the team in Teams.

**Copilot prompt to build it:**
> "When a file is created in my SharePoint folder called Enigma-Knowledge, send a Teams message to the Enigma channel saying: 'New document uploaded: [file name] by [author]. Review when you have a chance.' Include a link to the file."

**Result:** Zero-effort team awareness. No more "did you see the new spec?" emails.

---

#### Flow B — Weekly Project Status Digest (25 min to build)

**Scenario:** Every Monday at 8am, collect all Jira issues updated in the last 7 days and send a formatted digest to the team Teams channel.

**Copilot prompt to build it:**
> "Every Monday at 8:00 AM, call the Jira REST API at [your-jira-url]/rest/api/2/search with the JQL filter 'project = HLP AND updated >= -7d' and send the results as a formatted table to the Enigma Teams channel."

**Then add:**
> "Format the table with columns: Issue Key, Summary, Status, Assignee, Updated Date"

**Result:** Everyone walks into Monday knowing what changed last week — without anyone writing the report.

---

#### Flow C — Approval Workflow for Technical Changes (30 min to build)

**Scenario:** When an engineer uploads a file tagged as "Change Request" to SharePoint, automatically route it for approval to the team lead, track the decision, and notify the submitter.

**Copilot prompt to build it:**
> "When a file is uploaded to SharePoint in the folder 'Change-Requests', start an approval process and send an approval request to [team lead email]. If approved, move the file to the 'Approved-Changes' folder and send a Teams notification. If rejected, notify the original submitter by email with the rejection reason."

**Result:** Formal change control that runs automatically. No tracking spreadsheet needed.

---

#### Flow D — Meeting Action Items to Planner (25 min to build)

**Scenario:** After every Teams meeting in the Enigma project, automatically create tasks in Microsoft Planner from the Copilot-generated action items.

**Copilot prompt to build it:**
> "When a Teams meeting ends and a Copilot meeting recap is available, extract the action items from the recap. For each action item, create a task in Microsoft Planner in the 'Enigma' plan, assign it to the mentioned person, and set the due date mentioned in the recap."

**Note:** This flow uses the Teams meeting recap API — verify with IT that meeting recap output is accessible via Power Automate in your tenant.

**Result:** Action items from every meeting automatically land in Planner. Nothing falls through the cracks.

---

### Debugging Flows with Copilot

When a flow fails, click the failed run → open the error → click **Copilot** in the panel:
- *"Why did this step fail?"*
- *"How do I fix this JSON parsing error?"*
- *"Show me what the variable contained at this step"*

Copilot explains the error and suggests the fix — no need to Google Power Automate documentation.

### Demo Script
> "I'm going to build an automation live in 2 minutes. Watch — no code."
>
> *[Open Power Automate → Describe it to design it]*
>
> *[Type]: "When a file is created in my Enigma SharePoint folder, send a Teams message to the channel with the file name and a link."*
>
> *[Copilot proposes the full flow in 15 seconds]*
>
> "Copilot built this from one sentence. I'll click Save and Test — and the next time any of us uploads a file to that folder, the whole team gets notified automatically."

### Effort Estimate
| Task | Time |
|------|------|
| Flow A: Document notification | 20 min |
| Flow B: Weekly digest | 25 min |
| Flow C: Approval workflow | 30 min |
| Flow D: Action items to Planner | 25 min |
| **Total (build all 4)** | **~100 min** |
| **POC demo (just Flow A)** | **~20 min** |

---

## Use Case 9 — Copilot Researcher: Deep Research for R&D

### What it does
**Researcher** is a specialized AI agent built into Microsoft 365 Copilot (available at copilot.microsoft.com). Unlike a regular chat, Researcher performs multi-step, multi-source research — searching the web AND your internal M365 documents simultaneously — and synthesizes the findings into a structured report with citations. Think of it as a research analyst available on demand.

As of April 2026, Researcher uses a **multi-model approach**: one model generates the research plan and retrieves sources, a second model independently critiques and validates the findings. This significantly reduces hallucination and improves source quality.

### Why it matters
> "In R&D, we spend hours researching competitive approaches, new standards, regulatory requirements, and technology options. Researcher does a first-pass literature synthesis in minutes — with citations — so I start from an informed position instead of a blank page."

### License Note
Researcher is included in your Copilot M365 license. Usage is shared with the Analyst agent: **25 combined queries per month** (per user). Use them for substantial research tasks, not quick questions — those belong in regular Copilot Chat.

### Where to Access
1. Go to [copilot.microsoft.com](https://copilot.microsoft.com) — sign in with your M365 account
2. In the left sidebar, find **Researcher** (pre-pinned)
3. Or: In Microsoft 365 Copilot Chat (Teams or copilot.microsoft.com), type `@Researcher` to invoke it

### Step-by-Step: R&D Research Tasks

#### Task 1 — Technology Assessment (most useful for R&D)

**When to use:** Evaluating a new technology, library, protocol, or approach before committing to it.

**Prompt pattern:**
> "Research the current state of [technology/approach] for [use case]. Cover: maturity level, key players or implementations, known limitations, adoption in enterprise environments, and any security or compliance considerations. Cite sources."

**Example for your context:**
> "Research OAuth2 implementation options for enterprise on-premises systems in 2025-2026. Cover: PKCE vs. implicit flow security considerations, integration with Active Directory, vendor support, and known vulnerabilities. Include citations from security standards bodies."

**What you get:** A structured 2-4 page report with headings, bullet points, and source links — ready to paste into a Word ADR or share with the team.

---

#### Task 2 — Competitive & Standards Intelligence

**Prompt pattern:**
> "Research what [competitors / industry standards bodies] are currently publishing about [topic]. Summarize the key trends, any recent changes to standards, and what implications they have for [your product/domain]."

**Example:**
> "Research current industry standards and emerging best practices for cybersecurity in B2C analytics platforms, specifically around data retention, access logging, and AI model transparency requirements. Focus on publications from 2024-2026."

---

#### Task 3 — Internal Knowledge Synthesis (uses your M365 data)

This is uniquely powerful: Researcher searches your emails, Teams conversations, SharePoint documents, and meeting transcripts — not just the web.

**Prompt pattern:**
> "Search our internal documents and communications for everything related to [topic]. Synthesize what decisions have been made, what's still open, and what was the last status."

**Example:**
> "Search our internal documents, emails, and Teams conversations for all discussions about the HLP module authentication approach. What decisions were made, who owns the implementation, and what open questions remain?"

**What you get:** A synthesis of your own organizational knowledge — the kind of institutional memory that normally lives only in people's heads.

---

#### Task 4 — Pre-Meeting Research Brief

**Prompt pattern:**
> "I have a meeting with [stakeholder/topic] in [timeframe]. Prepare a research brief covering: background on [topic], recent relevant developments, key questions I should ask, and any risks or dependencies I should raise."

---

### Two Research Modes (April 2026)

| Mode | How it works | Best for |
|------|-------------|----------|
| **Critique Mode** (default) | Two models: one generates, one critiques. Higher accuracy. | Technical research, standards, decisions |
| **Council Mode** | Multiple models respond side-by-side, showing where they agree/diverge | Controversial topics, design tradeoffs, strategic decisions |

To switch modes: in the Researcher interface, click the mode selector before submitting your query.

### Demo Script
> "We're evaluating a new integration approach for our next release. Normally I'd spend 3-4 hours reading documentation and vendor comparisons. Watch what Researcher does in 90 seconds."
>
> *[Open copilot.microsoft.com → Researcher]*
>
> *[Paste a technical research prompt]*
>
> *[Researcher returns a structured report with 8-10 cited sources]*
>
> "This is not a summary of one article. It synthesized 12 sources — web and our internal documents — and flagged where sources disagreed. The citations are live links. I can now go deep on any section. First pass in 90 seconds instead of 4 hours."

### Effort Estimate
| Task | Time |
|------|------|
| Access Researcher + first query | 10 min |
| Run 2-3 R&D research prompts | 20 min |
| **Total** | **~30 min** |

---

## Use Case 10 — Microsoft Loop: Collaborative R&D Workspace

### What it does
Microsoft Loop is a collaborative canvas — part document, part whiteboard, part task board — where the whole team works on the same content simultaneously, and Copilot can generate, rewrite, and organize content within it. Unlike a shared Word document, Loop components are live and can be embedded directly in Teams chats, Outlook emails, and meetings.

### Why it matters
> "Design reviews, sprint retrospectives, risk brainstorms — these are all collaborative. Loop lets the whole team contribute in real time, with Copilot helping structure and summarize what we write together. No more 'who has the latest version of the doc?'"

### Where to Access
- [loop.microsoft.com](https://loop.microsoft.com) — browser
- Teams → Loop app (left sidebar)
- Inline in Teams chat: type `/loop` to insert a Loop component

### Step-by-Step: 3 R&D Loop Workspaces to Build

#### Workspace 1 — Sprint Planning Board (20 min to set up)

1. Go to [loop.microsoft.com](https://loop.microsoft.com) → **+ New workspace** → name it `Enigma Sprint Planning`
2. Add a **Table** component — columns: Task | Owner | Priority | Sprint | Status | Notes
3. Click **Copilot** in the page → **Suggest content**:
   > "Based on common R&D sprint tasks for a cybersecurity analytics project, suggest 10 typical backlog items with priorities"
4. Team members edit the table in real time — changes appear for everyone instantly
5. Share the workspace to the Enigma Teams channel — the table is now embedded in Teams

#### Workspace 2 — Risk Register (15 min to set up)

1. New Loop page: `Enigma Risk Register`
2. Ask Copilot:
   > "Create a risk register table with columns: Risk ID | Description | Probability (H/M/L) | Impact (H/M/L) | Mitigation | Owner | Status. Add 5 example rows typical for an R&D cybersecurity project."
3. Team populates and updates it live during risk reviews
4. Embed in monthly status meeting agenda

#### Workspace 3 — Decision Log (15 min to set up)

1. New Loop page: `Enigma Decision Log`
2. Ask Copilot:
   > "Create a decision log table: Decision ID | Date | Description | Rationale | Decision Maker | Alternatives Considered | Status"
3. After each architecture or design meeting, paste the action items and ask Copilot:
   > "Format these meeting notes as decision log entries: [paste notes]"

### Loop + Teams Integration (the key differentiator)

The real power: Loop components live inside Teams conversations.

1. In a Teams channel, click **+** → **Loop component**
2. Choose: Table, Checklist, Voting table, or Agenda
3. The component appears in the chat — everyone can edit it without leaving Teams
4. When the meeting ends, the component retains all edits — no copy-paste into a doc needed

**Use in your next design review:**
- Share a Loop agenda before the meeting (via Teams)
- During the meeting, everyone adds notes and action items directly to the Loop component
- After the meeting, the component is the minutes — already shared, already updated

### Demo Script
> "Let me show you how a design review works now versus how it worked before."
>
> "Before: I create a Word doc, email it for review, get 4 different versions back, manually merge them."
>
> *[Open Loop → show the sprint planning table already filled in by multiple people]*
>
> "Now: one canvas, everyone edits at the same time, Copilot helps structure the content. The document is always current. There is no version 2."

### Effort Estimate
| Task | Time |
|------|------|
| Create 3 workspaces | 20 min |
| Populate with Copilot-suggested content | 15 min |
| Connect to Teams channel | 10 min |
| **Total** | **~45 min** |

---

## Use Case 11 — Copilot Analyst: Data Insights from Internal Sources

### What it does
**Analyst** is the companion agent to Researcher (also at copilot.microsoft.com). While Researcher focuses on research synthesis from web + documents, Analyst specializes in **quantitative analysis** — examining structured data, identifying trends, and producing charts and tables from your organizational data. It can work with Excel files, SharePoint lists, and M365 usage data.

### Why it matters
> "I have metrics scattered across Excel files, Jira exports, and email threads. Analyst pulls it together and answers questions like 'where are we burning the most time?' or 'which workstream is trending the wrong way?' — in seconds, with a chart."

### License Note
Same as Researcher: **25 combined Researcher + Analyst queries per month** per user. Use for substantial analytical tasks.

### Step-by-Step: 3 Analyst Tasks for R&D

#### Task 1 — Schedule Variance Analysis

1. Export your Excel planning file to SharePoint (already done in UC3)
2. Open [copilot.microsoft.com](https://copilot.microsoft.com) → **Analyst**
3. Attach the Excel file
4. Prompt:
   > "Analyze this project schedule. For each workstream, calculate the variance between planned start and actual start. Identify which workstreams are behind by more than 2 weeks. Generate a bar chart showing schedule variance by workstream."

**Output:** Chart + table + narrative summary. Paste directly into your status PowerPoint.

---

#### Task 2 — Sprint Velocity Tracking

1. Export your last 4 sprint reports from Jira (CSV export)
2. Attach to Analyst
3. Prompt:
   > "Analyze sprint velocity over the last 4 sprints. Show story points planned vs. completed per sprint. Identify any trend (improving, declining, stable). Suggest 2-3 hypotheses for the trend based on the data."

---

#### Task 3 — Email Volume & Response Pattern Analysis

1. Analyst can query your Outlook data directly (no export needed)
2. Prompt:
   > "Analyze my email patterns for the last 30 days. How many emails do I receive per day by project or sender domain? What is my average response time? Which threads have the most back-and-forth? Suggest where I could reduce email volume."

**Output:** A personal productivity insight report — excellent data for the management ROI slide.

### Analyst vs. Copilot in Excel — When to Use Which

| Scenario | Use This |
|----------|----------|
| Analyzing your existing Excel planning file | Copilot in Excel (UC3) |
| Cross-source analysis (Excel + Jira + email) | Analyst agent |
| Generating a chart for a presentation | Either — Analyst produces publication-ready charts |
| Explaining a formula to a colleague | Copilot in Excel |
| Building an ROI or trend analysis for management | Analyst agent |

### Demo Script
> "Management wants to know where we're behind and why. Before I had to manually build this analysis. Watch Analyst do it."
>
> *[Open Analyst → attach Excel export + Jira CSV]*
>
> *[Type]: "Show schedule variance by workstream and identify the top 3 risk areas."*
>
> *[Analyst returns a chart and narrative in ~30 seconds]*
>
> "This took 30 seconds. The chart is already formatted for a presentation. The narrative explains the numbers. I'm done."

### Effort Estimate
| Task | Time |
|------|------|
| Export data to SharePoint | 10 min |
| Run 3 analysis prompts | 20 min |
| **Total** | **~30 min** |

---

## Presentation Plan: 2-Week Sprint

### Week 1 — Build

| Day | Task | Use Case |
|-----|------|----------|
| Mon | Create SharePoint folder + upload Enigma docs | UC1 |
| Mon-Tue | Build Copilot Studio agent, test in Teams | UC1 |
| Tue | Set up Outlook rules + folder structure | UC5 |
| Tue | Practice Copilot email features on real emails | UC5 |
| Wed | Save Excel to SharePoint, test Copilot in Excel prompts | UC3 |
| Wed | Run first Researcher query on a real R&D topic | UC9 |
| Thu | Build Power Automate Flow A (document notification) | UC8 |
| Thu | Build Power Automate Jira flow (basic query) | UC2 |
| Fri | Excel → Word → PowerPoint full pipeline | UC4 |
| Fri | Test Teams transcription in a real meeting | UC6 |

### Week 2 — Polish and Present

| Day | Task | Use Case |
|-----|------|----------|
| Mon | Copilot in Word: generate one ADR or meeting minutes | UC7 |
| Mon | Build Power Automate Flow B (weekly digest) | UC8 |
| Tue | Create 3 Loop workspaces, connect to Teams channel | UC10 |
| Tue | Run Analyst on Excel + Jira export data | UC11 |
| Wed | Full dry run — priority 6 use cases end-to-end | All |
| Thu | Refine based on dry run; prepare ROI metrics slide | All |
| Fri | **Presentation Day** | All |

### Recommended Presentation Flow (25-30 min)

Choose 6-7 use cases for the live demo. The full 11 can be referenced as "available and built."

```
[2 min]  Opening: Why AI Champion? What Copilot M365 actually is.
[5 min]  UC1:  Project Knowledge Agent — live Teams demo
                → "Ask the agent a real project question"
[4 min]  UC9:  Researcher — run a live technical research query
                → "Compare two approaches we're currently evaluating"
[4 min]  UC5:  Outlook — show folder structure + thread summary + Copilot reply
[3 min]  UC3+4: Excel analysis → PowerPoint generation (live pipeline)
[3 min]  UC8:  Power Automate — build a flow live in 90 seconds
[2 min]  UC6:  Teams meeting recap (show pre-recorded example)
[2 min]  UC10: Loop — show the sprint planning board in Teams
[1 min]  UC11: Analyst — show schedule variance chart from Excel data
[3 min]  Next steps: team rollout plan + quotas + support resources
```

**Tip for management audience:** Lead with UC9 (Researcher) after UC1 — the ROI story for research time saved is immediately understood by any manager.

---

## Metrics to Show Management

Use these numbers to build the ROI slide:

| Activity | Tool | Before Copilot | After Copilot | Saved/Week |
|----------|------|---------------|--------------|------------|
| Finding project information | UC1: Knowledge Agent | 15 min × 3/day | 10 sec | ~5 hrs |
| Email triage and response | UC5: Outlook Copilot | 90 min/day | 45 min/day | ~3.75 hrs |
| Meeting notes + action items | UC6: Teams recap | 45 min × 4/week | 5 min | ~2.7 hrs |
| Status deck creation | UC3+4: Excel→PPT | 2 hrs/week | 20 min | ~1.7 hrs |
| Jira queries + reporting | UC2: Flow + REST | 30 min/day | 5 min/day | ~2 hrs |
| Technical research | UC9: Researcher | 4 hrs/task × 2/week | 30 min | ~7 hrs |
| Recurring manual automations | UC8: Power Automate | 30 min/day | 0 min | ~2.5 hrs |
| Collaborative planning sessions | UC10: Loop | 60 min/session × 2 | 30 min | ~1 hr |
| Data analysis for reports | UC11: Analyst | 60 min/week | 10 min | ~50 min |
| Technical documentation drafts | UC7: Word Copilot | 90 min/doc | 20 min | ~1.2 hrs |
| **Total per person** | | | | **~27 hrs/week** |
| **10-person team** | | | | **~270 hrs/week** |

> Adjust these numbers with your actual experience during the POC week — real data from your own usage is far more compelling than estimates.

---

## Appendix: Useful Copilot Prompts Reference Card

Print or share this with your team after the presentation.

### Copilot in Teams
- `"Summarize this conversation"`
- `"What decisions were made in the last meeting?"`
- `"Draft a message to [person] asking for status on [topic]"`

### Copilot in Outlook
- `"What emails received today need my response?"`
- `"Summarize all unread emails since yesterday 5pm, grouped by urgency."`
- `"Summarize this thread. What do I need to do?"`
- `"Create a To Do task for each action item in this email."`
- `"Draft a reply agreeing and confirming I'll deliver by [date]."`
- `"Improve the tone — make it more collaborative, less directive."`
- `"Find emails from [name] about [topic] sent in [month]."`
- `"Schedule a 1-hour meeting with [name] about [topic] next week."`
- `"Who hasn't replied to my email about [topic] yet?"`
- `"Summarize the attachment in this email."` ← PDF/Word/PPT only

### Copilot in Excel
- `"Which rows have the longest schedule gap?"`
- `"Create a summary table of workstream status"`
- `"Highlight all rows where end date is past today"`

### Copilot in PowerPoint
- `"Create a presentation from [Word file]"`
- `"Add a timeline slide for these milestones: [list]"`
- `"Redesign this slide to be more visual, less text"`

### Copilot in Word
- `"Write an ADR from these notes: [bullets]"`
- `"Summarize this document in 5 bullets"`
- `"Make this section more formal and concise"`

### Copilot Studio (Agent)
- `"What was the architecture decision for [module]?"`
- `"Find all documents related to [topic]"`
- `"Summarize the project risks mentioned in our documents"`

### Power Automate (Copilot flow builder)
- `"When a file is created in [SharePoint folder], notify [Teams channel] with the file name and link"`
- `"Every Monday at 8am, send a summary of Jira issues updated in the last 7 days to [Teams channel]"`
- `"When a file is uploaded to [Change-Requests], start an approval to [manager], then move it to [Approved folder]"`
- `"After a Teams meeting ends, create Planner tasks from the Copilot recap action items"`

### Copilot Researcher (copilot.microsoft.com → Researcher)
- `"Research [technology/protocol] for enterprise use. Cover maturity, limitations, security considerations, and cite sources."`
- `"What are the current industry standards for [topic] in 2025-2026? Summarize key changes since 2023."`
- `"Search our internal documents and emails for all discussions about [topic]. What decisions were made and what is still open?"`
- `"Prepare a research brief for my meeting about [topic]: background, key questions to ask, risks to raise."`

### Copilot Analyst (copilot.microsoft.com → Analyst)
- `"Analyze this project schedule. Show variance between planned and actual per workstream. Generate a bar chart."`
- `"Analyze sprint velocity over the last 4 sprints. Identify the trend and suggest hypotheses."`
- `"Analyze my Outlook email patterns for the last 30 days. Where am I spending the most communication time?"`

### Microsoft Loop (loop.microsoft.com)
- `"Create a sprint planning table with columns: Task, Owner, Priority, Sprint, Status, Notes. Add 10 typical R&D tasks."`
- `"Create a risk register for a cybersecurity R&D project with 5 example risks."`
- `"Format these meeting notes as decision log entries: [paste notes]"`

---

## Quick Reference: Which Tool for Which Job?

| I want to... | Use this |
|-------------|----------|
| Ask a question about project documents | UC1: Knowledge Agent (Teams) |
| Query Jira without writing JQL | UC2: Power Automate + Jira REST |
| Ask questions about my Excel plan | UC3: Copilot in Excel |
| Generate a status presentation | UC4: Copilot in PowerPoint |
| Manage email overload | UC5: Outlook Rules + Copilot |
| Get meeting summaries and action items | UC6: Teams Copilot + Recap |
| Draft a spec, ADR, or meeting minutes | UC7: Copilot in Word |
| Automate a repetitive manual task | UC8: Copilot in Power Automate |
| Research a technology or standard | UC9: Copilot Researcher |
| Collaborate on a live document with the team | UC10: Microsoft Loop |
| Analyze data across multiple sources | UC11: Copilot Analyst |
