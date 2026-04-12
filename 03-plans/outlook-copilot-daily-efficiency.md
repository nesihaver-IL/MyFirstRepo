# Outlook 365 Copilot — Daily Efficiency Playbook
## Hands-On Guide for High-Volume Email Environments

**Owner:** AI Champion, R&D Division
**Date:** April 2026
**License Required:** Microsoft 365 Copilot (assigned)
**Problem it solves:** Too many emails during the day → nothing gets missed → clean end-of-day

---

## The Core Problem This Guide Solves

You are busy all day. Emails arrive continuously across multiple projects and systems.
By end of day you have:
- Unread emails with action items buried in threads
- Things you were CC'd on that may or may not need your attention
- Tasks that were implied in emails but never formally created
- No clear picture of what happened today and what needs your attention tomorrow

**This guide builds a system that does the triage for you** — so instead of spending your attention on email all day, you check in at two defined moments and let Copilot + automation handle everything in between.

---

## Your New Daily Email Rhythm

```
07:30 AM  → Morning Briefing (5 min)
           Scheduled Copilot prompt delivers overnight summary
           + today's priorities + meetings to prepare for

DURING DAY → Copilot rules + prioritization run silently
           High-priority emails surface automatically
           CC and system emails routed to background folders

05:00 PM  → End-of-Day Report (10 min)
           Power Automate delivers your daily digest:
           action items, flagged emails, unanswered threads,
           tasks created today, what needs attention tomorrow
```

---

## PART 1 — Morning Briefing (Scheduled Copilot Prompt)

### What it does
A scheduled Copilot prompt runs every morning at 7:30 AM, analyzes your overnight emails, calendar, and pending tasks, then delivers a structured briefing to your Teams or email — before you even open Outlook.

### Setup (15 min)

#### Step 1 — Access Scheduled Prompts
1. Go to [copilot.microsoft.com](https://copilot.microsoft.com) — sign in with your M365 account
2. Click the **clock icon** (Schedule) in the left sidebar, OR go to **Copilot Chat** and look for **Scheduled prompts**
3. Click **+ New scheduled prompt**

#### Step 2 — Create Morning Briefing Prompt
- **Name:** `Morning Briefing — R&D`
- **Schedule:** Daily, weekdays only, 7:30 AM
- **Notification:** Email + Teams notification when ready
- **Prompt text (copy this exactly, then personalize):**

```
Good morning. Please prepare my daily briefing:

1. EMAILS: Summarize unread emails received since yesterday 5 PM.
   Group by: (a) needs my response, (b) FYI only, (c) system/Jira alerts.
   For each email needing response, give me: sender, subject, and one-line summary.

2. MEETINGS: List today's meetings. For each one:
   - What is the topic?
   - Is there relevant recent email context I should know?
   - Do I need to prepare anything?

3. TASKS: What tasks in To Do or Planner are due today or overdue?

4. FOLLOW-UPS: Are there any emails I sent in the last 3 days
   that have not been replied to yet?

Format the output as a clean numbered list. Keep it under 300 words.
```

#### Step 3 — Verify it works
- Save the scheduled prompt
- You can click **Run now** to test it immediately
- The output arrives as a notification in Teams and/or your email inbox at 7:30 AM
- You have **max 10 scheduled prompts** per user — reserve the others for afternoon and end-of-day use

> **Pro tip:** Run the prompt manually for 3-5 days first. Adjust the wording based on what output you actually want. Then switch to scheduled.

---

## PART 2 — End-of-Day Report (Power Automate Flow)

### What it does
Every day at 5:00 PM, a Power Automate flow runs automatically. It collects:
- All emails flagged during the day (your "needs action" signals)
- Unanswered emails where you are in the To field (not CC)
- Tasks created in To Do today
- A count of emails received vs. processed

It formats all of this into a clean HTML email and sends it to yourself — your personal end-of-day digest.

### Setup (35 min)

#### Step 1 — Open Power Automate
1. Go to [make.powerautomate.com](https://make.powerautomate.com)
2. Click **+ Create** → **Describe it to design it** (Copilot mode)
3. Type:

```
Every weekday at 5:00 PM, get all emails I received today in Outlook
where I am in the To field (not CC), and that are still unread or flagged.
Format them as an HTML table with columns: Time, From, Subject, Flag Status.
Then get all tasks I created in Microsoft To Do today.
Send me an email to my own address with subject "End of Day Report — [today's date]"
containing both the email table and the task list.
```

4. Copilot proposes the flow — review the structure
5. Set connections: Office 365 Outlook, Microsoft To Do

#### Step 2 — Manual refinement (if needed)
If the Copilot-built flow needs adjustment, edit these steps manually:

**Trigger:**
- `Recurrence` → Interval: 1, Frequency: Day, Start time: 17:00, Time zone: your local zone
- Days of week: Monday, Tuesday, Wednesday, Thursday, Friday

**Action 1 — Get emails:**
- `Get emails (V3)` — Outlook connector
- Folder: Inbox
- Filter: `isRead eq false or flag/flagStatus eq 'flagged'`
- Top: 50
- Fetch Only Unread Messages: No (we want flagged too)

**Action 2 — Get tasks:**
- `List tasks` — Microsoft To Do connector
- List: Tasks
- Filter: created today (use expression: `formatDateTime(utcNow(),'yyyy-MM-dd')`)

**Action 3 — Create HTML table:**
- `Create HTML table` — Data Operations connector
- From: Output of Get emails
- Columns: Manual → From, Subject, ReceivedDateTime, Flag/FlagStatus

**Action 4 — Send email:**
- `Send an email (V2)` — Outlook connector
- To: your own email
- Subject: `End of Day Report — @{formatDateTime(utcNow(),'dd MMM yyyy')}`
- Body: HTML combining both tables (see template below)

#### Step 3 — Email body template
Paste this into the Body field of the Send email action (HTML mode):

```html
<h2>🌅 End of Day Report — @{formatDateTime(utcNow(),'dddd, dd MMMM yyyy')}</h2>

<h3>📬 Emails Needing Attention</h3>
<p>Unread or flagged emails where you are in the To field:</p>
@{body('Create_HTML_table')}

<h3>✅ Tasks Created Today</h3>
<p>Items you added to To Do today:</p>
@{body('Create_HTML_table_2')}

<h3>📊 Quick Stats</h3>
<p>
  Total unread / flagged emails in digest: @{length(body('Get_emails')?['value'])}<br/>
  Tasks logged today: @{length(body('List_tasks')?['value'])}<br/>
  Report generated: @{formatDateTime(utcNow(),'HH:mm')} local time
</p>

<hr/>
<p style="color:gray;font-size:11px;">
  This report was generated automatically by Power Automate + Copilot M365.<br/>
  To stop receiving it, disable the "End of Day Report" flow at make.powerautomate.com.
</p>
```

#### Step 4 — Test and activate
1. Click **Save** → **Test** → **Manually** → Run
2. Check your inbox for the report
3. Review: Are the right emails appearing? Is the format readable?
4. Adjust filters if needed (e.g., add CC emails for certain senders)
5. When satisfied: enable the flow and set it to run daily

---

## PART 3 — Inbox Triage System (Copilot Prioritization + Rules)

### 3A — Enable Copilot Inbox Prioritization (5 min)

This is a native Copilot feature in the new Outlook. It automatically scores every incoming email as High / Normal / Low priority based on: sender relationship, your job context, email content, and whether action is required.

1. Open **new Outlook** (desktop or web)
2. Go to **Settings** (gear icon) → **Mail** → **Copilot** → **Prioritize my inbox**
3. Toggle ON: **Prioritize my inbox**
4. Click **Customize priorities** and tell Copilot:
   - Who are your most important senders? (add names/roles)
   - What topics always need your attention? (e.g., "HLP", "production issue", "deadline")
   - What can be deprioritized? (e.g., newsletters, noreply, automated)
5. **Important:** High-priority emails appear with a colored marker in your inbox. Low-priority ones are visually de-emphasized.

> Review the priority assignments for 2-3 days and correct any misfires through the **feedback thumbs** on each email — Copilot learns from your corrections.

### 3B — Rule Stack (10 min to configure all 8)

These rules work together with Copilot prioritization. Configure in: **Settings → Mail → Rules → + Add new rule**

---

**Rule 1: Project Enigma — Inbox**
```
Condition:  Subject contains "HLP" OR "Enigma" OR "HLP-"
Action:     Move to folder: Projects/Enigma
            AND mark as important
Exception:  From = [your manager] → keep in Inbox top
```

---

**Rule 2: Jira Notifications → Background**
```
Condition:  From contains "jira" OR "atlassian" OR "@your-jira-domain"
Action:     Move to folder: Tools/Jira-Alerts
            AND mark as read
Why:        Jira sends notification floods. Check this folder
            twice/day from your digest, not continuously.
```

---

**Rule 3: CI/CD and System Alerts → Background**
```
Condition:  From contains "noreply" OR "jenkins" OR "gitlab"
            OR "monitoring" OR "alert@"
Action:     Move to folder: Tools/System-Alerts
            AND mark as read
```

---

**Rule 4: CC'd Emails (FYI) → Separate folder**
```
Condition:  My name is in CC field (not To)
Action:     Move to folder: FYI
            AND do NOT mark as read (you want to see the count)
Exception:  From = [manager] OR subject contains "urgent"
            → keep in Inbox
Review:     Check FYI folder only at 9am and 4pm
```

---

**Rule 5: Manager → Always surface**
```
Condition:  From = [manager's email address]
Action:     Categorize as "High Priority" (red category)
            AND move to top of Inbox
            AND play sound notification
```

---

**Rule 6: External Senders (outside your domain) → Flag**
```
Condition:  Sender's domain is NOT your company domain
Action:     Categorize as "External" (blue category)
Purpose:    External emails often have deadlines or require formal responses.
            Easy visual scan for external commitments.
```

---

**Rule 7: Large CC Thread Collapse**
```
Condition:  My name is in CC AND number of recipients > 5
Action:     Move to folder: FYI/Large-Threads
            AND mark as read
Purpose:    Large group CC threads are almost never actionable.
            You'll catch what matters in the morning briefing summary.
```

---

**Rule 8: Newsletters and Subscriptions → Weekly Review**
```
Condition:  Subject contains "Unsubscribe" OR "newsletter"
            OR from contains "marketing@" OR "news@"
Action:     Move to folder: Reading/Newsletters
            AND mark as read
Review:     Once per week, Friday afternoon, or delete if unused
```

---

### 3C — Folder Structure (Set up once, use forever)

```
📥 Inbox
    (only: direct To emails, high-priority flagged by rules)

📂 Projects/
    📁 Enigma/
    📁 [Project 2]/
    📁 [Project 3]/

📂 Tools/
    📁 Jira-Alerts/        ← check 2× per day
    📁 Confluence/
    📁 System-Alerts/      ← check 1× per day (or via digest)

📂 FYI/                    ← CC'd to you
    📁 Large-Threads/

📂 Reading/
    📁 Newsletters/        ← weekly review

📂 Action-Required/        ← manually flagged items you will act on
📂 Waiting-For/            ← emails you replied to, awaiting response
📂 Archive/                ← processed, no longer needed
```

**Quick-filing shortcuts:** Use `Ctrl+Shift+V` (Windows) to quickly move an email to any folder while reading it.

---

## PART 4 — Task Extraction from Emails

### 4A — Single Email: Extract Tasks with Copilot (instant)

When you open any email:
1. Click the **Copilot** button in the reading pane header
2. The Copilot panel opens with a thread summary
3. Under the summary, look for **Suggested tasks** or **Action items**
4. Click any suggested task → it opens in **Microsoft To Do** pre-filled with:
   - Task title (from the email subject/action phrase)
   - Due date (if detected in the email)
   - Link back to the source email
5. Adjust due date, set priority, add notes → **Save**

---

### 4B — Bulk Inbox Session: Extract All Action Items (daily habit)

Once per day (ideal: after lunch, 30-min focus), open Copilot Chat in Outlook or Teams:

**Prompt 1 — Scan for open actions:**
```
Look at my unread emails received in the last 24 hours
where I am in the To field. List all action items assigned to me,
with: sender, subject, action required, and deadline if mentioned.
Format as a numbered list, most urgent first.
```

**Prompt 2 — Convert to tasks:**
```
For each of the action items above, create a task in Microsoft To Do.
Set priority based on the urgency you detected.
Add the email sender and date as a note on each task.
```

**Prompt 3 — Check what you sent but got no reply on:**
```
Show me emails I sent in the last 5 business days
that have not received a reply. List: recipient, subject, date sent.
```

---

### 4C — Flag + Copilot Workflow (while reading email)

The fastest habit to build:
- While reading an email: press `Insert` key (or click the flag icon) to flag it
- At the end of the day, flagged emails auto-appear in **Flagged email** view (View → To-Do Bar → Flagged Emails)
- Open Copilot Chat and ask:
```
Show me all my flagged emails and create a To Do task for each one.
Use the email subject as the task title. Set due date to tomorrow unless
the email mentions a specific deadline.
```

---

### 4D — Power Automate: Auto-Create Tasks from Flagged Emails (set-and-forget)

Build this flow once — it runs automatically forever:

**In Power Automate (Copilot mode), describe:**
```
When an email in Outlook is flagged, create a task in Microsoft To Do
in the "Action Required" list with the task title equal to the email subject,
the note equal to the sender's name and the first 200 characters of the email body,
and a reminder set for tomorrow at 9 AM.
```

**Flow structure Copilot will build:**
```
Trigger:  When email is flagged (Outlook V3)
Action 1: Create task (Microsoft To Do)
          - Title: Subject of email
          - Body: "From: [sender] | [first 200 chars of body]"
          - Due: addDays(utcNow(), 1)
          - Reminder: tomorrow 9:00 AM
```

Once this flow is running:
- You flag an email → a task appears in To Do automatically → no manual task creation needed

---

### 4E — Escalate to Planner (team-visible tasks)

When an action item involves your team (not just you):

1. In Copilot Chat (after extracting action items from an email), say:
```
Create a Planner task for [action item description] in the Enigma plan,
assign it to [team member name], set priority to High, due [date].
```

2. Or: From the email thread summary, click **Create task** → select **Planner** (not To Do)
   - Choose the plan
   - Assign and set due date
   - The task appears on the team board — visible to everyone

---

## PART 5 — Advanced Copilot Email Features

### 5A — Thread Summarization (beyond the basics)

When you open a long thread, click **Summary by Copilot** at the top. The summary includes:
- **Key points** — decisions and facts, with numbered citations linking to the exact message
- **Open questions** — unanswered questions detected in the thread
- **Action items** — assigned tasks with owner names and deadlines
- **Reply with Copilot** — a pre-composed reply addressing the action items

**Advanced prompts to use after reading the summary:**
```
"What is my specific role in this thread? What do I need to do?"
"Has a decision been made on [topic]? When and by whom?"
"Draft my reply accepting the timeline and confirming I'll prepare the document."
"Translate this thread to English." (if multilingual team)
```

---

### 5B — Attachment Summarization

When an email contains a PDF, Word, or PowerPoint attachment:
1. In the reading pane, hover over the attachment
2. Click **Summarize** (Copilot icon next to the file name)
3. Copilot shows a summary panel with key points from the document
4. Ask follow-up questions: *"What are the open action items in this document?"*

> **Works with:** PDF, .docx, .pptx
> **Does NOT work with:** Encrypted files, files with sensitivity labels, .xlsx, .csv
> **Requires:** New Outlook (not Classic Outlook)

---

### 5C — Natural Language Email Search

In the new Outlook, the search bar has been enhanced with Copilot:

1. Click the search bar → type in plain English (not keywords):
   - *"Emails from John about the HLP integration last month"*
   - *"Emails where I was asked to approve something"*
   - *"Attachments containing the word 'architecture' sent this year"*
   - *"All emails about the Q3 FAT test plan"*
2. Copilot shows an AI summary of the results + individual emails
3. You can continue with follow-up questions in the search results panel

> **Tip:** Use this instead of folder-diving when you know roughly what you're looking for but not exactly where it is.

---

### 5D — Copilot Email Coaching (before sending)

Before sending any important email:
1. Write your draft in the compose window
2. Click **Copilot** in the compose toolbar → **Coaching by Copilot**
3. Copilot scores your email on three dimensions:

| Dimension | What it checks |
|-----------|---------------|
| **Tone** | Too formal? Too casual? Collaborative or directive? |
| **Clarity** | Is the ask clear? Are there ambiguous phrases? |
| **Reader sentiment** | How will the recipient likely interpret this? |

4. Read the suggestions — apply the ones that improve the message
5. Especially useful for: escalations, client-facing emails, conflict resolution emails, requests to management

---

### 5E — Smart Scheduling from Email

When a meeting is discussed in an email thread:
1. In the email reading pane, click **Copilot** → **Schedule meeting**
2. Copilot:
   - Reads the thread to understand the meeting purpose
   - Pre-fills title, agenda, and suggested attendees
   - Checks all attendees' free/busy slots
   - Proposes 3 time options that work for everyone
3. You confirm → meeting invite sent automatically

**Or use Copilot Chat in Outlook:**
```
"Schedule a 1-hour design review with [name1] and [name2] next week.
 Use the email thread about HLP authentication as the meeting agenda.
 Avoid Monday morning and Friday afternoon."
```

---

### 5F — Automatic Rescheduling (new in 2026)

Copilot now monitors your calendar for conflicts and proposes fixes:
1. When a high-priority meeting is added that conflicts with an existing appointment, Copilot sends you a notification: *"This meeting conflicts with [existing meeting]. Reschedule?"*
2. Click **Let Copilot find a new time** → it proposes alternatives for the lower-priority meeting
3. One click to send the reschedule request

**Enable this:** Settings → Calendar → Copilot → Automatic scheduling suggestions → On

---

## PART 6 — Viva Insights: Focus Time & Work Pattern Protection

### What Viva Insights adds (that Copilot doesn't)

Copilot is reactive (helps when you ask). Viva Insights is proactive (monitors your patterns and alerts you).

| Feature | What it does |
|---------|-------------|
| **Focus time booking** | Automatically blocks 2-4 hours per day in your calendar for deep work |
| **Collaboration hours** | Shows how much time you spend in meetings vs. focused work |
| **Wellbeing nudges** | Reminds you to take breaks; flags when you're working outside hours |
| **Top collaborator insights** | Who are you spending the most communication time with? |
| **Quiet hours** | Delays email sends and mutes notifications outside working hours |

### Enable Focus Time Booking (10 min)

1. Open **Microsoft Teams** → left sidebar → **Viva Insights** (add it if not there: click `...` → search Viva Insights)
2. Go to **Protect time** tab
3. Click **Focus plan** → Enable
4. Configure:
   - **Hours per day:** 2 hours (recommended minimum)
   - **Preferred time:** Morning (9-11am) for deep work, or afternoon (2-4pm) for uninterrupted coding/analysis
   - **Teams status:** Set to "Do Not Disturb" during focus time
   - **Mute Teams notifications:** Yes
5. Viva starts booking focus blocks 2 weeks ahead on a rolling basis
6. **These blocks appear in your Outlook calendar** and protect you from meeting invites during that time

> **R&D-specific tip:** Protect your morning block for design/coding work. Block 2pm-4pm for deep analysis. Leave flexible slots at 11am and 4pm for reactive team communication.

---

### Enable Quiet Hours (8 min)

Prevent emails you compose late in the evening from creating pressure on colleagues:

1. In Viva Insights → **Settings** → **Quiet hours**
2. Set your working hours (e.g., 8am-6pm)
3. Enable **Delay email send** — emails composed outside those hours are held and sent at the start of the next business day
4. Enable **Quiet time notification** — Viva reminds you when you're about to disrupt someone's off-hours

---

## PART 7 — Copilot Studio: Personal Email Agent (Advanced)

### What it does
Build a Copilot Studio agent with access to your Outlook mailbox that you can query at any time in natural language. More powerful than scheduled prompts because it can take actions, not just summarize.

> **Note:** Custom Outlook agents in Copilot Studio became available starting March 2026. Your tenant may still be in rollout. Check availability at [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com).

### What this agent can do
- *"What emails need my response today?"* → lists unread emails with action items
- *"Draft a reply to [sender] telling them I'll deliver by Friday"* → drafts and queues the reply
- *"Move all Jira alerts from today to the Jira folder"* → executes folder management
- *"Create tasks from all flagged emails in my inbox"* → batch creates To Do tasks
- *"Who hasn't replied to my email about the HLP spec?"* → searches sent items

### Build Steps (45 min)

#### Step 1 — Create the agent
1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. **+ Create** → **New agent**
3. Name: `My Email Assistant`
4. Description: *"I manage your Outlook inbox, extract tasks, draft replies, and give you daily summaries."*

#### Step 2 — Add Actions
1. In the agent, go to **Actions** tab
2. Click **+ Add action** → **Add from connector**
3. Search: **Office 365 Outlook**
4. Add these action groups:
   - `Get emails` — read inbox
   - `Send an email` — send/reply
   - `Flag email` — flag for follow-up
   - `Move email to folder` — organize
   - `Create event` — schedule from email context
5. Also add: **Microsoft To Do** → `Create task`

#### Step 3 — Add Instructions
```
You are a personal email assistant for [your name], an R&D engineer at Cognyte.

You have access to their Outlook inbox and Microsoft To Do.

Your primary jobs:
1. TRIAGE: When asked, read recent emails and identify what needs a response,
   what is FYI only, and what has action items.
2. DRAFT: When asked to reply, draft a professional, concise email.
   Always confirm the draft before sending.
3. ORGANIZE: Move, flag, or categorize emails when asked.
4. TASKS: Create To Do tasks from action items found in emails.
   Always include the sender's name and email date in the task note.

Rules:
- Never send an email without explicit confirmation from the user ("yes, send it")
- When unsure about an action, ask for clarification first
- Keep all summaries concise — bullet points, not paragraphs
- Flag anything involving: deadlines, approvals, or senior leadership
```

#### Step 4 — Publish to Teams
1. **Publish** → **Microsoft Teams**
2. Pin the agent to your Teams sidebar for instant access
3. Now you can chat with it like a personal assistant throughout the day

### Example conversation
```
You:   What emails in my inbox need my response today?

Agent: You have 4 emails needing response:
       1. [Sarah] re: HLP architecture review — needs your approval on approach
       2. [IT Admin] re: VPN renewal — confirmation required by tomorrow
       3. [Manager] re: Q3 status update — asked for slides by Friday
       4. [Client] re: demo scheduling — asked for 3 available time slots

You:   Draft a reply to Sarah agreeing to her approach and confirming
       I'll join the review call Thursday at 2pm.

Agent: Here is a draft:
       "Hi Sarah, thanks for the write-up. The OAuth2 with SSO approach
       looks solid — I agree with the decision. I'll join the review call
       on Thursday at 2pm. Let me know if you need anything from my side
       before then. Best, [your name]"

       Shall I send this?

You:   Yes, send it.

Agent: Sent. ✓
```

---

## Daily Checklist: Your 15-Minute Email Routine

### Morning (5 min — before opening Outlook)
- [ ] Read Scheduled Copilot briefing (arrives in Teams/email at 7:30 AM)
- [ ] Note 1-2 highest priority items requiring action today
- [ ] Check To Do for due tasks (auto-populated from yesterday's flagging)

### Midday (5 min — after lunch)
- [ ] Quick scan: Inbox only (rules have already cleared the noise)
- [ ] Flag anything that needs action (→ auto-creates To Do task via flow)
- [ ] Ask Copilot Chat: *"Any urgent emails since this morning that need my response?"*

### End of Day (5 min — before closing)
- [ ] Read End-of-Day Report (arrives automatically at 5 PM)
- [ ] Review task list in To Do: mark completed, defer anything that slipped
- [ ] Ask Copilot Chat: *"Who am I waiting for a reply from? Any follow-ups I should send?"*
- [ ] Close Outlook — you're done for the day

---

## Quick Reference: Copilot Prompt Card for Outlook

Print and keep this at your desk or pin it in Teams.

### Triage
```
"What emails received today need my response?"
"Summarize all unread emails since yesterday 5pm, grouped by urgency."
"Which emails did I send that have not been replied to yet?"
"Show me everything flagged in my inbox."
```

### Summarize
```
"Summarize this thread. What do I need to do?"
"What decision was made in this conversation and when?"
"Summarize the attachment in this email."
"What are the open questions in this thread?"
```

### Compose & Reply
```
"Draft a reply agreeing and confirming I'll deliver by [date]."
"Reply professionally declining and suggesting next week instead."
"Write an email to [person] asking for the status of [topic]. Keep it under 5 sentences."
"Improve the tone of this email — make it more collaborative, less directive."
```

### Tasks
```
"Create a To Do task for each action item in this email."
"Create tasks from all my flagged emails, due tomorrow."
"Show me my overdue tasks and help me prioritize them."
```

### Search
```
"Find emails from [name] about [topic] sent in [month]."
"Show me emails where I was asked to approve something."
"Find all emails mentioning the HLP authentication module."
```

### Schedule
```
"Schedule a 1-hour meeting with [name] next week about [topic]."
"Use this email thread as the agenda for a meeting. Find a time next week."
"What conflicts do I have this week that I should resolve?"
```

---

## Setup Sequence: Do These in Order

| Step | What | Time | Where |
|------|------|------|-------|
| 1 | Create folder structure in Outlook | 10 min | Outlook |
| 2 | Configure 8 inbox rules | 20 min | Outlook Settings → Rules |
| 3 | Enable Copilot inbox prioritization | 5 min | Outlook Settings → Copilot |
| 4 | Create morning briefing scheduled prompt | 15 min | copilot.microsoft.com |
| 5 | Build End-of-Day Report flow | 35 min | make.powerautomate.com |
| 6 | Build Flagged Email → To Do task flow | 20 min | make.powerautomate.com |
| 7 | Enable Viva Insights focus time booking | 10 min | Teams → Viva Insights |
| 8 | Build Email Assistant agent (optional) | 45 min | copilotstudio.microsoft.com |
| **TOTAL** | | **~2.5 hrs** | |

---

## What to Demo in the Presentation

Show these 4 things live — they are the most visually compelling:

1. **Morning briefing output** — show the actual scheduled prompt result (run it manually live)
   > *"This is what I read instead of opening my inbox at 7:30 every morning."*

2. **Thread summarization + task creation** — open a real 15-message thread, summarize, click task
   > *"15 messages. 10 seconds. One task. Done."*

3. **End-of-Day Report email** — show the Power Automate output in your inbox
   > *"Every day at 5pm this arrives. I know exactly what I didn't get to and what's waiting."*

4. **Natural language search** — search for something you "can't remember exactly where"
   > *"I knew it was about HLP and from last month. One search. Found it."*
