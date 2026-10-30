# Status: Structure for Jira Team Video

Last updated: 2026-10-30 (animation build in progress)

## Current phase

P0 (decide and access), partly done.

| Phase | State |
|---|---|
| P0. Decide and access | Edition decided (Data Center), language decided (English). Narration, hosting: open |
| P1. Trial and verification | Not started. Needs a Data Center trial instance |
| P2. Script and storyboard | Draft in PLAN.md |
| P3. Sample project | Not started |
| P4. Screen capture | Not started |
| P5. Animation and edit | Built: `video/` (HyperFrames, 107 s, placeholder palette, illustrative screens). Brand swap and P1 verification still pending |
| P5b. Synthetic voice | Done: local Kokoro voice am_michael, 11 scene clips in `video/assets/` |
| P5c. Render | Done: `video/renders/structure-for-jira-team-video.mp4` (1:47, 1920x1080, H.264 + AAC, 8.7 MB). Not committed (renders/ is gitignored) |
| P6. Voice and captions | Not started |
| P7. Review and fix | Not started |
| P8. Publish and test | Not started |

## Decisions log additions

- 2026-10-30: Narration = synthetic voice, local Kokoro (am_michael), no external service.
- 2026-10-30: Palette = neutral placeholder in `video/index.html` :root, to be replaced with Cognyte brand values.
- 2026-10-30: Length = about 1:47 (plan said about 6.5 min). The plan's extra time was for real screen demos, which need a trial instance. Chapters and tips (D2) are the next cut.
- 2026-10-30: Workflow = general-video (companion). The faceless-explainer and general-video workflow skills were retired upstream; their guidance now lives in /hyperframes references.
- 2026-10-30: Usage check (`npx hyperframes usage --json`) returned status unknown (unsupported_auth). Not guessed.

## Blockers

1. Cognyte brand template (blocks final look, not the build): cognyte.com is blocked by the cloud session's
   network policy. Official assets must be supplied (see BRAND.md).
2. Data Center trial access for the screen recording (P1).
3. Hosting location for the finished clip.

## Decisions log

- 2026-10-30: Edition = Jira Data Center. Language = English only.
- 2026-10-30: GSAP vendored locally (video/assets/vendor/gsap.min.js, 3.15.0) because the CDN is blocked in the cloud session; the first render failed on this and was fixed.
- 2026-10-30: Plan lives in this repo under 02-work/structure-for-jira-video/.

## Next actions

- Owner: provide the Cognyte brand kit (BRAND.md) and Data Center trial access.
- Claude: once access is confirmed, run P1 and update the verification table in PLAN.md.
