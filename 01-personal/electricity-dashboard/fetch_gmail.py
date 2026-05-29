#!/usr/bin/env python3
"""
fetch_gmail.py — שולף חשבוניות חשמל מ-Gmail ומייצר נתוני JSON
==================================================================
דרישות:
    pip install google-auth google-auth-oauthlib google-api-python-client pypdf2

שימוש:
    1. הצב את קובץ credentials.json בתיקייה זו
    2. הרץ: python fetch_gmail.py
    3. בדפדפן שייפתח — אשר גישה לחשבון Gmail שלך
    4. הנתונים יישמרו ב-electricity_data.json
    5. פתח את index.html — הדשבורד יטעון את הנתונים אוטומטית
"""

import os
import json
import base64
import re
from datetime import datetime
from pathlib import Path

# ── Google API ──────────────────────────────────────────────────────────────
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── PDF reading ─────────────────────────────────────────────────────────────
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    try:
        import pypdf as PyPDF2
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False
        print("⚠️  pypdf/PyPDF2 לא מותקן — קריאת PDF לא תהיה זמינה")
        print("   הרץ: pip install pypdf")

# ── הגדרות ──────────────────────────────────────────────────────────────────
SCOPES        = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_FILE    = 'credentials.json'
TOKEN_FILE    = 'token.json'
OUTPUT_FILE   = 'electricity_data.json'
PDFS_DIR      = 'electricity_pdfs'

# מונחי חיפוש — מיילים מחברת חשמל
SEARCH_QUERY  = (
    '(from:iec.co.il OR from:חשמל OR subject:חשבון-חשמל OR subject:"חשבון חשמל")'
    ' after:2025/01/01'
)

# ── דפוסי regex לחילוץ מידע מ-PDF ──────────────────────────────────────────
AMOUNT_PATTERNS = [
    r'סה["\u05b4]?כ\s+לתשלום[:\s]+([0-9,]+\.?[0-9]*)',
    r'לתשלום[:\s]+([0-9,]+\.?[0-9]*)\s*[₪ש"ח]',
    r'חוב\s+נוכחי[:\s]+([0-9,]+\.?[0-9]*)',
    r'([0-9,]+\.?[0-9]*)\s*ש["\u05b4]?ח',
    r'(\d{3,6})\s*₪',
]

DATE_PATTERNS = [
    r'תאריך\s+חשבון[ית]?[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
    r'תקופת\s+חיוב[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
    r'(\d{1,2}[./]\d{1,2}[./](?:20\d{2}))',
]


def authenticate() -> object:
    """אימות OAuth 2.0 מול Google"""
    import webbrowser
    creds = None

    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(CREDS_FILE).exists():
                print(f"\n❌ קובץ {CREDS_FILE} לא נמצא!")
                print("   הוראות:")
                print("   1. היכנס ל: https://console.cloud.google.com")
                print("   2. צור פרויקט חדש (או בחר קיים)")
                print("   3. APIs & Services → Enable APIs → Gmail API")
                print("   4. APIs & Services → Credentials → Create OAuth 2.0 Client ID")
                print("   5. Application type: Desktop app")
                print("   6. הורד את ה-JSON ושמור כ: credentials.json בתיקייה זו")
                raise FileNotFoundError(f"חסר: {CREDS_FILE}")

            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)

            # Try browser first, fallback to manual URL entry for WSL2
            webbrowser._tryorder = []  # Disable browser detection
            try:
                creds = flow.run_local_server(port=0)
            except:
                # Manual flow for WSL2/headless
                print("\n" + "="*70)
                print("🔗 OAuth Authentication Required")
                print("="*70)
                auth_url, _ = flow.authorization_url()
                print(f"\n📱 Open this URL in your Windows browser:\n")
                print(f"   {auth_url}\n")
                print("📝 Steps:")
                print("   1. Sign in with your Gmail account")
                print("   2. Click 'Allow'")
                print("   3. You'll be redirected. Copy the 'code' parameter")
                print("   4. Paste it below\n")

                # Input validation: OAuth codes are alphanumeric, slash, dash, underscore
                auth_code = input("🔑 Enter authorization code: ").strip()
                if not auth_code or not re.match(r'^[a-zA-Z0-9/_\-]+$', auth_code):
                    raise ValueError("❌ Invalid authorization code format. Expected alphanumeric + / - _")
                if len(auth_code) < 10:
                    raise ValueError("❌ Authorization code too short. Check you copied the full code.")

                creds = flow.fetch_token(code=auth_code)

        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        print(f"✅ אימות הצליח — token נשמר ב-{TOKEN_FILE}")

    return creds


def fetch_messages(service, query: str) -> list:
    """שולף רשימת מזהי הודעות לפי שאילתה"""
    messages = []
    result = service.users().messages().list(userId='me', q=query, maxResults=200).execute()
    messages.extend(result.get('messages', []))

    while 'nextPageToken' in result:
        result = service.users().messages().list(
            userId='me', q=query,
            pageToken=result['nextPageToken'], maxResults=200
        ).execute()
        messages.extend(result.get('messages', []))

    print(f"📬 נמצאו {len(messages)} הודעות")
    return messages


def get_message_detail(service, msg_id: str) -> dict:
    """שולף פרטי הודעה מלאים"""
    return service.users().messages().get(
        userId='me', id=msg_id, format='full'
    ).execute()


def extract_pdf_from_message(msg: dict) -> list[bytes]:
    """מחלץ קבצי PDF מצורפים מהודעה"""
    pdfs = []

    def walk_parts(parts):
        for part in parts:
            mime = part.get('mimeType', '')
            filename = part.get('filename', '')

            if mime == 'application/pdf' or filename.lower().endswith('.pdf'):
                body = part.get('body', {})
                data = body.get('data')
                if data:
                    pdfs.append(base64.urlsafe_b64decode(data))
                elif 'attachmentId' in body:
                    # attachment stored separately
                    pdfs.append(('attachment_id', body['attachmentId'], msg['id']))

            if 'parts' in part:
                walk_parts(part['parts'])

    payload = msg.get('payload', {})
    if 'parts' in payload:
        walk_parts(payload['parts'])

    return pdfs


def fetch_attachment(service, msg_id: str, att_id: str) -> bytes:
    """שולף קובץ מצורף לפי ID"""
    att = service.users().messages().attachments().get(
        userId='me', messageId=msg_id, id=att_id
    ).execute()
    return base64.urlsafe_b64decode(att['data'])


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """מחלץ טקסט מ-PDF"""
    if not PDF_SUPPORT:
        return ""
    try:
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"  ⚠️  שגיאה בקריאת PDF: {e}")
        return ""


def parse_amount(text: str) -> float | None:
    """מחלץ סכום לתשלום מטקסט"""
    for pattern in AMOUNT_PATTERNS:
        m = re.search(pattern, text)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                continue
    return None


def parse_date(text: str, email_date: str) -> tuple[int, int]:
    """מחלץ חודש ושנה מטקסט או ממטא-נתוני המייל"""
    for pattern in DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            try:
                raw = m.group(1)
                for fmt in ('%d/%m/%Y', '%d.%m.%Y', '%d/%m/%y', '%d.%m.%y'):
                    try:
                        d = datetime.strptime(raw, fmt)
                        return d.year, d.month
                    except ValueError:
                        continue
            except Exception:
                continue

    # fallback — תאריך מהמייל עצמו
    try:
        # RFC 2822 format from Gmail headers
        from email.utils import parsedate_to_datetime
        d = parsedate_to_datetime(email_date)
        return d.year, d.month
    except Exception:
        return None, None


def get_email_date(msg: dict) -> str:
    """שולף את תאריך המייל מהכותרות"""
    headers = msg.get('payload', {}).get('headers', [])
    for h in headers:
        if h['name'].lower() == 'date':
            return h['value']
    return ''


def build_data_structure(records: list[dict]) -> dict:
    """בונה מבנה נתונים לפי שנה וחודש"""
    years = {}
    for rec in records:
        year = rec.get('year')
        month = rec.get('month')
        amount = rec.get('amount')
        if not all([year, month, amount]):
            continue
        if year not in years:
            years[year] = [None] * 12
        years[year][month - 1] = amount

    return years


def main():
    print("🔌 שולף חשבוניות חשמל מ-Gmail...")
    print("=" * 50)

    # אימות
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # יצירת תיקיית PDF
    Path(PDFS_DIR).mkdir(exist_ok=True)

    # שליפת מיילים
    messages = fetch_messages(service, SEARCH_QUERY)
    if not messages:
        print("⚠️  לא נמצאו מיילים. נסה לשנות את SEARCH_QUERY בסקריפט.")
        return

    records = []

    for i, msg_ref in enumerate(messages):
        msg = get_message_detail(service, msg_ref['id'])
        email_date = get_email_date(msg)
        print(f"\n[{i+1}/{len(messages)}] מעבד הודעה מ-{email_date[:16]}...")

        pdf_list = extract_pdf_from_message(msg)

        for pdf_item in pdf_list:
            # אם attachment_id
            if isinstance(pdf_item, tuple) and pdf_item[0] == 'attachment_id':
                pdf_bytes = fetch_attachment(service, pdf_item[2], pdf_item[1])
            else:
                pdf_bytes = pdf_item

            text = extract_text_from_pdf_bytes(pdf_bytes)
            amount = parse_amount(text)
            year, month = parse_date(text, email_date)

            if amount:
                print(f"  ✅ חודש {month}/{year} — {amount:,.0f} ₪")
                records.append({'year': year, 'month': month, 'amount': amount})

                # שמור PDF
                fname = f"{year}-{month:02d}-{amount:.0f}.pdf"
                (Path(PDFS_DIR) / fname).write_bytes(pdf_bytes)
            else:
                print(f"  ⚠️  לא נמצא סכום ב-PDF")

        # גם אם אין PDF — ננסה לחלץ מגוף המייל
        if not pdf_list:
            body_text = extract_body_text(msg)
            amount = parse_amount(body_text)
            year, month = parse_date(body_text, email_date)
            if amount:
                print(f"  ✅ (מגוף המייל) חודש {month}/{year} — {amount:,.0f} ₪")
                records.append({'year': year, 'month': month, 'amount': amount})

    if not records:
        print("\n❌ לא נמצאו נתונים. בדוק את שאילתת החיפוש.")
        return

    # בנה מבנה נתונים
    data = build_data_structure(records)

    # שמור JSON
    output = {
        'generated_at': datetime.now().isoformat(),
        'records_found': len(records),
        'data': data,
    }
    Path(OUTPUT_FILE).write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n✅ נשמרו {len(records)} רשומות ב-{OUTPUT_FILE}")

    # סיכום לפי שנה
    print("\n📊 סיכום:")
    for year, months in sorted(data.items()):
        values = [v for v in months if v is not None]
        total = sum(values)
        print(f"  {year}: {len(values)} חשבוניות | סה\"כ {total:,.0f} ₪ | ממוצע {total/len(values):,.0f} ₪/חודש")

    print(f"\n🌐 פתח את index.html לצפייה בדשבורד")


def extract_body_text(msg: dict) -> str:
    """מחלץ טקסט מגוף המייל"""
    def walk(parts):
        texts = []
        for part in parts:
            mime = part.get('mimeType', '')
            if mime in ('text/plain', 'text/html'):
                data = part.get('body', {}).get('data', '')
                if data:
                    texts.append(base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore'))
            if 'parts' in part:
                texts.extend(walk(part['parts']))
        return texts

    payload = msg.get('payload', {})
    parts = payload.get('parts', [payload])
    texts = walk(parts)
    return '\n'.join(texts)


if __name__ == '__main__':
    main()
