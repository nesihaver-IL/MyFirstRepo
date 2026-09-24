# Background music

Drop one audio file here named exactly:

```
background.mp3
```

That's it — the page already has a 🎵 button wired up to play/pause it on
loop. No further setup needed.

## A few notes

- **You need the rights to use the track.** If it's a song you bought or
  a track from a royalty-free library (e.g. Pixabay Music, YouTube Audio
  Library), you're covered for a personal page like this. Don't use an
  arbitrary copyrighted commercial song without checking its license —
  and note that pulling the audio out of a streaming service like
  Spotify isn't a legitimate way to get the file, regardless of intent.
- **It doesn't start the instant the page loads.** No browser allows
  unmuted audio to play before the visitor has interacted with the page
  at all — this is a deliberate anti-annoyance policy (strictest on
  Safari/iOS), not something this page can override. Instead, playback
  starts on the visitor's very first tap/click anywhere on the page, so
  it feels close to immediate once they start scrolling or tapping a
  photo. The 🎵 button still shows the current state and lets them
  pause or restart it manually at any time.
- When someone opens a video, the background music automatically pauses
  (so it doesn't play over the video's own sound) and resumes once they
  close it.
- Keep the file reasonably small (a compressed MP3, a few MB) so it
  doesn't slow down the page for visitors on mobile data.
