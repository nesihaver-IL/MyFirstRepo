# טסלה רודסטר: ההדגמה מ-15 באוקטובר 2026 - מצגת לכיתה ו׳

מצגת בעברית (5 שקפים, PPTX) על ההדגמה של טסלה רודסטר: מה נראה, איך זה עובד (לפי המידע הזמין), ומתי הרכב צפוי להגיע לשוק הפרטי. בשקף 3 מוטמעת אנימציה קצרה (36 שניות) שממחישה את ההדגמה. זו איור, לא צילום.

## קבצים
- `tesla-roadster-kids.pptx` - המצגת
- `video/roadster-demo-animation.mp4` - האנימציה (1280x720, H.264)
- `video/poster.png` - תמונת פתיחה לאנימציה בתוך המצגת
- `make_animation.py` - מייצר את האנימציה (Pillow + ffmpeg)
- `build_deck.py` - בונה את המצגת (python-pptx)

## בנייה מחדש
```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python make_animation.py     # דורש ffmpeg במערכת
ffmpeg -ss 3 -i video/roadster-demo-animation.mp4 -frames:v 1 video/poster.png
.venv/bin/python build_deck.py
```

## מקורות (נבדקו בחיפוש, לא מול מקור ראשוני)
- CNN, 16 באוקטובר 2026: https://www.cnn.com/2026/10/16/world/video/tesla-unveils-what-it-says-is-a-flying-car
- Statesman (תוכן בסגנון AP): https://www.statesman.com/business/article/tesla-roadster-mcgregor-flying-car-musk-spacex-22480443.php
- Aviation Week, סילוני הגז: https://aviationweek.com/aerospace/emerging-technologies/tesla-demos-flying-roadster-powered-spacex-cold-gas-thrusters
- Fox News: https://www.foxnews.com/tech/tesla-roadster-flies-flips-hits-60-mph-flash
- NBC News, עיכובים קודמים: https://www.nbcnews.com/tech/tech-news/elon-musk-shows-flying-tesla-roadster-years-delays-rcna603905

## מה לא מופיע בשקפים, בכוונה
- מספר הסילונים: המקורות לא מסכימים (10 פתחים לפי מוסק, 4 מאחור ועוד 6 בגרסת Rocket לפי דיווח אחר).
- זמן 0-60 (0.81 שנייה לפי טסלה ו-Aviation Week, "פחות משנייה" לפי מוסק) ומהירות מקסימלית (230 מייל לשעה לפי מוסק): טענות של החברה בלבד.
- "הדגמה ללא נהג": מופיע רק במקורות משניים.

## לפני ההצגה - לבדוק
- מוסק אמר שייצור ללקוחות יתחיל ב-2028, ואין הבטחה לאספקה. יש לבדוק את עדכוני ההשקה באתר טסלה.
- ה-FAA לא אישר את הרכב לפי CNN. יש לבדוק שוב, כי המצב עלול להשתנות.
- המידע מהחיפוש שלי ועלול להיות חלקי. יש לאמת לפני הצגה.
- הטמעת הסרטון ב-PowerPoint דורשת קודק H.264 (נתמך בדרך כלל). אם הוא לא מתנגן, הפעילו את הקובץ הנפרד.
