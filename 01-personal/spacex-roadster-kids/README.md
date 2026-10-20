# Tesla Roadster בטיסת Falcon Heavy - מצגת לכיתה ו׳

מצגת בעברית (5 שקפים, PPTX) על טיסת הניסוי הראשונה של Falcon Heavy (6 בפברואר 2018), שבה הטיל מכונית Tesla Roadster עם בובה בשם Starman. בשקף 3 מוטמע סרטון אנימציה קצר (36 שניות).

## קבצים
- `falcon-heavy-kids.pptx` - המצגת
- `video/falcon-heavy-animation.mp4` - הסרטון (1280x720, H.264). אנימציה המבוססת על המקורות, לא צילום אמיתי.
- `video/poster.png` - תמונת פתיחה לסרטון בתוך המצגת
- `make_animation.py` - מייצר את הסרטון (Pillow + ffmpeg)
- `build_deck.py` - בונה את המצגת (python-pptx)

## בנייה מחדש
```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python make_animation.py     # דורש ffmpeg במערכת
ffmpeg -ss 2 -i video/falcon-heavy-animation.mp4 -frames:v 1 video/poster.png
.venv/bin/python build_deck.py
```

## מקורות (נבדקו בחיפוש, לא מול אתר SpaceX)
- השיגור, התאריך ומתחם השיגור: https://planeandpilotmag.com/spacex-launches-falcon-heavy-rocket/ ו-https://www.pressreader.com/usa/albuquerque-journal/20180207/281595240984804
- המטען (Roadster ו-Starman) והשיקול של מאסק במשקל: https://www.nbcchicago.com/news/national-international/spacex-falcon-heavy-first-launch/2041756/
- נחיתת הבוסטרים הצדדיים והחטאת הבוסטר המרכזי: https://thedailyworld.com/?p=16224 ו-https://lunarcabin.com/Rocket_Launches/falconheavydemo_1.html
- המסלול של המכונית: https://orbitcodex.com/operations/demo-flight-1-maiden-flight-falcon-heavy
- 27 מנועים ושלושה בוסטרים (מקור משני): https://weatherboy.com/?p=4675

## לפני ההצגה - לבדוק
- **לא אומת:** המוזיקה ("Space Oddity") שהתנגנה במכונית, ולוח המעגל עם הטקסט על המכונית. הוסרו מהמצגת עד שיימצא מקור ראשוני.
- המספרים (27 מנועים, "הרקטה החזקה ביותר") מבוססים על מקור משני. יש לאמת מול spacex.com.
- המידע הוא מהידע והחיפוש שלי ועלול להיות לא מעודכן. יש לאמת לפני הצגה.
- הטמעת הסרטון ב-PowerPoint דורשת קודק H.264 (נתמך בדרך כלל). אם הוא לא מתנגן, הפעילו את הקובץ הנפרד.
- הפונט Arial תומך בעברית ב-Windows וב-macOS.
