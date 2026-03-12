---
name: sora-distribution
description: >
  End-to-end workflow for Sora creators who want to organize, schedule, and distribute their AI-generated video library to social media platforms (TikTok, Instagram, X/Twitter) using Metricool. Use this skill whenever a Sora creator mentions distributing, scheduling, or posting their Sora videos, managing a Sora video library, bulk uploading to TikTok/Instagram/X, or setting up a social media content calendar from Sora content. Also trigger when someone mentions organizing AI-generated videos, cleaning up video libraries, or batch scheduling short-form video content. This skill covers the full pipeline: library organization → video review/categorization → Google Drive hosting → URL extraction → Metricool CSV creation → bulk import.
---

# Sora Creator Distribution Pipeline

This skill walks you through the complete workflow to go from a raw folder of downloaded Sora videos to a fully scheduled social media content calendar — with minimal daily involvement after setup.

> **Note:** This skill was built for [@thesoragirls](https://www.tiktok.com/@thesoragirls), an AI pop group, and uses `thesoragirls` / `SoraGirls` as placeholder values throughout — including in `scripts/build_schedule.py` and the Google Apps Script (`scripts/get_drive_links.gs`, where the output sheet is named `SoraGirls_DriveLinks`). Before starting, ask the user for their group name and cross-platform handle so you can swap these out. For example: *"This skill uses `@thesoragirls` and `SoraGirls` as example placeholders in a few places. What's your group name and handle so I can update them?"*

## Overview

The pipeline has 5 stages:
1. **Organize** — rename and categorize your video library
2. **Review** — watch and label each clip
3. **Host** — upload to Google Drive for public URLs
4. **Build** — generate a Metricool-compatible schedule CSV
5. **Import** — bulk-load into Metricool and publish

Read the full reference at `references/pipeline.md` before starting. The helper scripts for stages 3–5 are in `scripts/`.

---

## Stage 1: Organize Your Library

Your downloaded Sora videos will have hash-based filenames like `19700121_0349_691af15288e.mp4`. Rename them to a consistent convention so everything is trackable:

**Naming format:** `SG_[SOURCE][TYPE][MEMBER]_[###].mp4`

- **SOURCE**: where it was downloaded from (e.g., `TSG` for your main account, `UA` for a secondary)
- **TYPE**: content type — `MV`, `CONCERT`, `VLOG`, `STUDIO`, `COMEDY`, `NARRATIVE`, `ACTIVITY`, `DANCE`, `SPORT`, `PROMO`, `EVENT`, `ART`
- **MEMBER**: who appears — `GROUP`, or individual member names
- **###**: zero-padded sequence number per type/member combo

**Ask the creator:**
- What are the source folder names (where did you download to)?
- Who are the members/characters in your group?
- What content types do you produce?

Build a master CSV tracker with these columns:
`new_filename, original_filename, source, content_type, members, caption, duration_sec, file_size_mb, notes, dest_folder`

The `notes` field is used to flag videos for deletion: add `[DELETE_CANDIDATE]` to exclude them from scheduling.

---

## Stage 2: Review & Categorize

Build an HTML review tool so the creator can watch each clip in the browser and label it. The tool should:
- Embed the video (using the local file path)
- Show current metadata (filename, caption, type, member)
- Let them edit caption, type, member inline
- Save changes back to the master CSV

Do this in batches if the library is large (100–200 clips per session). After each session, update the master CSV.

**Key fields to collect per video:**
- Caption (what you'd actually post)
- Content type
- Member(s) featured
- Flag for deletion if not postable

---

## Stage 3: Host on Google Drive

Metricool requires a **publicly accessible URL** for each video. Google Drive works well.

**Step 1 — Upload your videos:**
Upload the entire organized folder to Google Drive. Make sure you're uploading the real video files (not 0-byte placeholders). Use Google Drive for Desktop for large batches — it's more reliable than browser drag-and-drop.

**Step 2 — Run the Apps Script to generate share links:**
1. Go to [script.google.com](https://script.google.com)
2. Create a new project, paste the script from `scripts/get_drive_links.gs`
3. Replace `PASTE_YOUR_FOLDER_ID_HERE` with the folder ID from your Drive URL
   - The folder ID is the long string after `/folders/` in the URL
4. Click **Run → getVideoLinks**
5. A new Google Sheet called `SoraGirls_DriveLinks` will be created in your Drive
6. Download it: **File → Download → CSV**

The script automatically makes every `.mp4` publicly viewable and outputs a two-column table: `filename, drive_url`.

---

## Stage 4: Build the Metricool Schedule CSV

Use `scripts/build_schedule.py` to generate the import-ready CSV.

**Before running, you'll need:**
- The master tracker CSV (with your 485 active videos)
- The DriveLinks CSV from Stage 3
- Answers to:
  - Which platforms? (TikTok / X / Instagram — or all three)
  - Start date?
  - Posts per day? (10/day is a strong cadence for growth)

**Caption cleaning rules baked into the script:**
- `@thesoragirls` (your actual cross-platform handle) stays as-is with the `@`
- All other Sora-platform handles (e.g., `@ava.girl`, `@crystal.party`) get stripped of `@` and dot-suffix, with the base name capitalized: `Ava`, `Crystal`
- If your group has a different handle, update `OFFICIAL_HANDLE` at the top of the script

**Posting times (default, 10/day):**
`07:00, 09:00, 11:00, 13:00, 15:00, 17:00, 19:00, 20:30, 22:00, 23:30`

These hit the main engagement windows across US time zones. Adjust in the script if needed.

**Hashtag logic:**
- All posts get `#AIMusic #AIPop` + a content-type tag (e.g., `#MusicVideo`, `#Vlog`)
- Group posts get `#[GroupName]`; solo posts get `#[GroupName] #[MemberName]`

Run the script and it will produce `Sora_Metricool_Schedule.csv`.

---

## Stage 5: Import to Metricool

1. Go to **Planning** in Metricool
2. Click the **⋮** (three dots) menu in the top right of the calendar
3. Select **Import CSV**
4. Upload `Sora_Metricool_Schedule.csv`
5. When prompted for date/time format, select **YYYY-MM-DD** and **HH:MM:SS**
6. Review the preview and confirm

**If the import fails:**
- Check that your Drive share links are working (open one in an incognito window)
- Make sure the video files in Drive are not 0 bytes — this means the upload didn't complete
- Verify the time format includes seconds (e.g., `07:00:00` not `07:00`)

---

## Ongoing Workflow

Once the backlog is scheduled, keep the pipeline going for new videos:

1. Download new Sora videos → add to master CSV with new filenames
2. Review captions and labels
3. Upload to same Google Drive folder
4. Re-run the Apps Script (it'll add new files to the sheet)
5. Run `build_schedule.py` for just the new batch, using a start date after your last scheduled post
6. Import the new CSV into Metricool

---

## Key Numbers to Track

- Total active videos in library
- Days of scheduled content remaining
- New videos added per day
- Platforms connected in Metricool

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Drive files show 0 bytes | Re-upload using Google Drive for Desktop, not browser drag-and-drop |
| Apps Script error: `Cannot read properties of null` | You ran it as a standalone script — it creates its own Sheet, so this shouldn't happen with the provided script |
| Metricool CSV format error | Verify column names match exactly — common mistakes: `Twitter` instead of `Twitter/X`, `Tiktok` instead of `TikTok`, missing seconds in time |
| Videos not posting on Instagram | Make sure `Instagram Post Type` is set to `REEL` for video content |
| Captions look wrong | Check caption cleaning rules in `build_schedule.py` and adjust the `OFFICIAL_HANDLE` variable |
