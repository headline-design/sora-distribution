# Sora Distribution Pipeline — Full Reference

## Who this is for

Sora creators who produce AI-generated video content and want to distribute it at scale across TikTok, Instagram, and X with minimal daily effort. The workflow assumes:
- You download videos directly from Sora to a local folder
- You have (or want) a Metricool account with TikTok, Instagram, and/or X connected
- You have a Google account for Drive hosting

---

## Tools Required

| Tool | Purpose | Cost |
|---|---|---|
| Metricool | Social media scheduler | Free tier covers most needs |
| Google Drive | Host videos for public URLs | Free (15GB) |
| Google Apps Script | Auto-generate Drive share links | Free (included with Google account) |
| Python 3 | Run the schedule builder script | Free |

Python packages needed: `openpyxl` (install with `pip install openpyxl`)

---

## Stage Details

### Stage 1: Library Organization

**Goal:** Every video has a unique, descriptive filename and a row in the master CSV.

**Master CSV columns:**
- `new_filename` — standardized name (e.g., `YG_TSG_MV_GROUP_001.mp4`)
- `original_filename` — the original Sora download name
- `source` — which account it came from
- `content_type` — one of the 12 content types
- `members` — which member(s) appear
- `caption` — what you'd post as the caption
- `duration_sec` — video length
- `file_size_mb` — file size
- `notes` — any notes; add `[DELETE_CANDIDATE]` to exclude from scheduling
- `dest_folder` — where the organized file lives

**Content types:** MV, CONCERT, VLOG, STUDIO, COMEDY, NARRATIVE, ACTIVITY, DANCE, SPORT, PROMO, EVENT, ART

**Tips:**
- Be consistent with member names — they drive hashtag logic
- The `notes` field is your safety valve — anything with `[DELETE_CANDIDATE]` gets skipped
- Run the organization in batches; don't try to do the whole library at once

---

### Stage 2: Video Review

**Goal:** Every active video has a caption and correct labels.

Build a simple HTML page that loops through your videos and lets you:
- Watch each clip
- Edit the caption
- Confirm or change the content type and member
- Flag for deletion

Save changes back to the master CSV after each session. Doing 100–200 clips per review session is sustainable. Three rounds of review is typical for a library of 500+ videos.

---

### Stage 3: Google Drive Hosting

**Why Drive?** Metricool's bulk CSV importer requires a publicly accessible URL for each video. Drive handles this cleanly at no cost for most library sizes.

**Upload tips:**
- Use Google Drive for Desktop (not browser) for large batches — it retries failed uploads automatically
- After uploading, spot-check a few files: right-click → "Get link" → open in incognito to confirm it streams
- If files show 0 bytes in Drive, the upload didn't complete — re-upload

**Apps Script (get_drive_links.gs):**
The script crawls the entire folder tree (including subfolders), makes each `.mp4` publicly viewable, and writes filename + share URL to a new Google Sheet. It takes a few minutes for large libraries.

To find your folder ID: open the Drive folder → look at the URL → copy the string after `/folders/`

---

### Stage 4: Building the Schedule CSV

**Key decisions to make upfront:**
- Start date (day 1 of posting)
- Posts per day (10/day = ~49 days per 485 videos)
- Which platforms (TikTok, Instagram, X)

**Caption cleaning:**
The script strips Sora-specific @handle formatting:
- Your official cross-platform handle (e.g., `@thesoragirls`) stays with the `@`
- Character/collab handles (e.g., `@ava.girl`) become first-name only (`Ava`)
- The rule is: anything with a dot-suffix (`.girl`, `.party`, `.bear`) is a Sora username — strip the `@` and suffix, capitalize the base

**Randomization:**
Videos are shuffled with a fixed random seed so the schedule has content variety (not all music videos first, then all vlogs, etc.) while being reproducible.

---

### Stage 5: Metricool Import

**Correct CSV format (critical):**
- Column name for X is `Twitter/X` (not `Twitter`)
- Column name for TikTok is `TikTok` (not `Tiktok`)
- Time format must include seconds: `07:00:00` (not `07:00`)
- Instagram videos should use `Instagram Post Type = REEL`
- TikTok privacy: `PUBLIC_TO_EVERYONE`

**Import steps:**
1. Planning → ⋮ menu → Import CSV
2. Upload the CSV
3. Set date format: `YYYY-MM-DD`
4. Set time format: `HH:MM:SS`
5. Review and confirm

**After import:**
Metricool will queue all posts. You can review them in the Calendar view and edit individual posts if needed.

---

## Ongoing Maintenance

Once the backlog is scheduled, new videos slot in at the end of your calendar:

1. Add new videos to the master CSV (continue the numbering sequence)
2. Upload new files to the same Drive folder
3. Re-run the Apps Script — it adds the new files to the DriveLinks sheet
4. Run `build_schedule.py` with `--start` set to the day after your last scheduled post
5. Import the new CSV

This keeps the calendar continuously stocked with about 1 minute of work per batch.

---

## Metricool Plan Considerations

The free Metricool plan has limits on scheduled posts. If you're scheduling 485 posts at once, check your plan's queue limit. If needed:
- Import in batches (e.g., 30 days at a time)
- Or upgrade to a plan that supports larger queues

---

## Common Mistakes

1. **Uploading the organized folder before confirming files have content** — always check file sizes before uploading to Drive
2. **Running the Apps Script as a standalone project** — use the version in `scripts/get_drive_links.gs` which creates its own spreadsheet
3. **Wrong column names in the CSV** — use the template in `scripts/build_schedule.py` which has the exact column names
4. **Not setting Instagram Post Type to REEL** — Instagram treats video posts differently; without this they may fail
5. **Forgetting seconds in the time column** — Metricool requires `HH:MM:SS`
