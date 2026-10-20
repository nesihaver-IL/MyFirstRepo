# Starship - מצגת לכיתה ו׳

מצגת בעברית (5 שקפים, PPTX) על Starship של SpaceX, עם סרטון אנימציה קצר (36 שניות) שמוטמע בשקף 3.

## קבצים
- `starship-kids.pptx` - המצגת
- `video/starship-animation.mp4` - הסרטון (1280x720, H.264)
- `video/poster.png` - תמונת פתיחה לסרטון בתוך המצגת
- `make_animation.py` - מייצר את הסרטון (Pillow + ffmpeg)
- `build_deck.py` - בונה את המצגת (python-pptx)

## בנייה מחדש
```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python make_animation.py     # דורש ffmpeg במערכת
ffmpeg -ss 2 -i video/starship-animation.mp4 -frames:v 1 video/poster.png
.venv/bin/python build_deck.py
```

## לפני ההצגה - לבדוק
- כל המספרים (גובה, עוצמה, מספר טיסות) הם הערכה מהידע שלי ולא אומתו מול מקור עדכני. בדקו ב-spacex.com ובדפי הטיסות של Starship.
- ייתכן שהמידע על Starship השתנה מאז מועד הידע שלי. יש לאמת לפני הצגה.
- הטמעת הסרטון ב-PowerPoint דורשת קודק H.264 (נתמך בדרך כלל). אם הסרטון לא מתנגן, הפעילו אותו מהקובץ הנפרד.
- הפונט Arial תומך בעברית ב-Windows וב-macOS. בדקו שהטקסט מיושר לימין.
