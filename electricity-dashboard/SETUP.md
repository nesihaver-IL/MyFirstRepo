# הגדרת גישה ל-Gmail — מדריך שלב אחר שלב

## שלב 1: התקנת חבילות Python

```bash
pip install -r requirements.txt
```

---

## שלב 2: יצירת פרויקט ב-Google Cloud Console

1. היכנס ל: https://console.cloud.google.com
2. לחץ **"Select a project"** → **"New Project"**
3. שם הפרויקט: `electricity-bills` → לחץ **Create**

---

## שלב 3: הפעלת Gmail API

1. בתפריט הצד: **APIs & Services** → **Library**
2. חפש: `Gmail API`
3. לחץ על **Gmail API** → לחץ **Enable**

---

## שלב 4: יצירת אישורי OAuth 2.0

1. **APIs & Services** → **Credentials**
2. לחץ **+ Create Credentials** → **OAuth client ID**
3. אם תתבקש — הגדר **OAuth consent screen**:
   - User Type: **External**
   - App name: `Electricity Bills`
   - Support email: הכנס את המייל שלך
   - שמור ועבור לשלב הבא
4. Application type: **Desktop app**
5. Name: `electricity-client`
6. לחץ **Create**
7. לחץ **Download JSON**
8. שנה שם הקובץ ל: `credentials.json`
9. העבר את הקובץ לתיקייה זו: `electricity-dashboard/`

---

## שלב 5: הרצת הסקריפט

```bash
cd electricity-dashboard
python fetch_gmail.py
```

בפעם הראשונה — יפתח דפדפן לאישור גישה:
- בחר את חשבון Gmail שלך
- לחץ **Allow**
- חזור לטרמינל

---

## שלב 6: צפייה בדשבורד

פתח את קובץ `index.html` בדפדפן.

הדשבורד יטעון את `electricity_data.json` שנוצר ויציג:
- **סיכום 2025 מול 2026**
- גרפי עמודות חודשיים
- טבלת פירוט עם שינויים

---

## פתרון בעיות

| שגיאה | פתרון |
|-------|--------|
| `credentials.json not found` | ודא שהקובץ נמצא בתיקייה `electricity-dashboard/` |
| `Access blocked` | הוסף את המייל שלך ב-OAuth consent screen → Test users |
| לא נמצאו מיילים | שנה את `SEARCH_QUERY` בסקריפט, נסה: `from:iec.co.il` |
| שגיאת PDF | ודא `pip install pypdf` הותקן |
