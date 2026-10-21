# טסלה רודסטר: ההדגמה מ-15 באוקטובר 2026 - מצגת לכיתה ו׳ (גרסה 2)

מצגת בעברית (8 שקפים, PPTX) על ההדגמה של טסלה רודסטר. המצגת עונה על ששת השאלות מדף העבודה: מה קרה, מתי ואיפה, מי מעורב, למה זה חשוב, מה אנחנו חושבים (דעה קבוצתית), ואיך מציגים את הסיפור בכל דרך. בשקף 5 מוטמעת אנימציה קצרה (42 שניות). זו איור, לא צילום.

## קבצים
- `tesla-roadster-kids.pptx` - המצגת
- `video/roadster-demo-animation.mp4` - האנימציה (1280x720, H.264)
- `video/poster.png` - תמונת פתיחה לאנימציה בתוך המצגת
- `images/musk.jpg` - (אופציונלי) תמונה של מאסק מרישיון פתוח. אם הקובץ לא קיים, השקף מציג מסגרת ריקה.
- `make_animation.py` - מייצר את האנימציה (Pillow + ffmpeg)
- `build_deck.py` - בונה את המצגת (python-pptx)

## בנייה מחדש
```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python make_animation.py     # דורש ffmpeg במערכת
ffmpeg -ss 3 -i video/roadster-demo-animation.mp4 -frames:v 1 video/poster.png
.venv/bin/python build_deck.py
```

## תמונה של אילון מאסק וסרטון רשמי
- **סרטון:** לא מוטמע, כי הוא חומר מוגן זכויות. השקף מקשר לסרטון ב-CNN.
- **תמונה:** לא הורדנו תמונה בגרסה הזו, כי הגישה לאתר Wikimedia Commons נחסמה בסביבת העבודה. יש להוריד תמונה מרישיון פתוח, לבדוק את הרישיון, לשמור כ-`images/musk.jpg` ולהוסיף קרדיט ב-`images/CREDIT.txt`, ואז להריץ שוב את `build_deck.py`.

## מקורות (נבדקו בחיפוש, לא מול מקור ראשוני)
- CNN, 16 באוקטובר 2026 (סרטון וקפיצה): https://www.cnn.com/2026/10/16/world/video/tesla-unveils-what-it-says-is-a-flying-car
- Statesman (תוכן בסגנון AP): https://www.statesman.com/business/article/tesla-roadster-mcgregor-flying-car-musk-spacex-22480443.php
- Drive Tesla Canada, מועד ההדגמה: https://driveteslacanada.ca/news/tesla-roadster-unveiling-livestream-october-15-2026/
- ARY News, דחייה מ-1 באוקטובר: https://arynews.tv/tesla-to-unveil-long-delayed-roadster-on-october-1-musk-says
- Aviation Week, סילוני הגז: https://aviationweek.com/aerospace/emerging-technologies/tesla-demos-flying-roadster-powered-spacex-cold-gas-thrusters
- i24NEWS (עברית): https://www.i24news.tv/he/news/science-and-technology/artc-28d73fdd
- ICE (עברית): https://www.ice.co.il/auto/news/article/1133858
- Electrek, דיווח על דחייה קודמת לאוגוסט: https://electrek.co/2026/06/05/tesla-roadster-demo-delayed-august-spacex-thruster/

## צבעים
צבע האדום בשקפים (#E82127) הוא הערך הנפוץ ביותר באתרי צבעי מותגים של צד שלישי, אבל לא אומת מול מדריך המותג הרשמי של טסלה. לפני שימוש רשמי, בדקו את הערך מול חומרי העיתונות של טסלה.

## מה לא מופיע בשקפים, בכוונה
- מספר הסילונים: המקורות לא מסכימים (10 פתחים לפי מאסק, 4 מאחור ועוד 6 בגרסת Rocket לפי דיווח אחר).
- זמן 0-60 (0.81 שנייה לפי טסלה ו-Aviation Week, "פחות משנייה" לפי מאסק) ומהירות מקסימלית: טענות של החברה בלבד.
- תפקידיו העדכניים של מאסק: הדיווחים לא תואמים זה את זה, ולכן כל התפקידים מסומנים לאימות.
- "עשיר מאוד": לא אומת במקור.

## לפני ההצגה - לבדוק
- מועד הייצור ללקוחות: מאסק אמר 2028, ללא הבטחה. ה-FAA לא אישר את הרכב לפי CNN. בדקו שוב את העדכונים באתר טסלה.
- הקישורים בשקף 7 עשויים להשתנות. בדקו שהם פעילים.
- דעת הקבוצה בשקף 6 צריכה להיכתב מחדש על ידי הקבוצה לפני ההצגה.
- הטמעת הסרטון ב-PowerPoint דורשת קודק H.264 (נתמך בדרך כלל). אם הוא לא מתנגן, הפעילו את הקובץ הנפרד.
