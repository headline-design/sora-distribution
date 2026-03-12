"""
Sora Distribution Pipeline — Metricool Schedule Builder
Generates a Metricool-compatible bulk import CSV from:
  - A master video tracker CSV
  - A Google Drive links CSV (from get_drive_links.gs)

USAGE:
  python build_schedule.py \
    --tracker path/to/Sora_Girls_Master_Tracker.csv \
    --links path/to/SoraGirls_DriveLinks.csv \
    --start 2026-03-11 \
    --posts-per-day 10 \
    --output Sora_Metricool_Schedule.csv

  OR for an xlsx DriveLinks file:
  python build_schedule.py \
    --tracker path/to/Sora_Girls_Master_Tracker.csv \
    --links path/to/SoraGirls_DriveLinks.xlsx \
    --start 2026-03-11 \
    --output Sora_Metricool_Schedule.csv
"""

import csv
import re
import random
import argparse
import os
from datetime import date, timedelta

# ─────────────────────────────────────────────
# CONFIGURE THESE FOR YOUR GROUP
# ─────────────────────────────────────────────

# Your official handle — the same across TikTok, X, Instagram, Sora
# This handle will be KEPT with its @ in captions.
# All other @handles will be stripped and capitalized.
OFFICIAL_HANDLE = 'thesoragirls'  # ← replace with your actual cross-platform handle (no @)

# Group name for hashtags (no spaces, no #)
GROUP_HASHTAG = 'SoraGirls'  # ← replace with your group's hashtag name (no #)

# Member hashtags — map your MEMBER column values to hashtag names
MEMBER_TAGS = {
    'GROUP':   f'#{GROUP_HASHTAG}',
    'UNKNOWN': f'#{GROUP_HASHTAG}',
    # Add your members here, e.g.:
    # 'AVA':     f'#{GROUP_HASHTAG} #Ava',
    # 'AMBER':   f'#{GROUP_HASHTAG} #Amber',
    # 'RAVEN':   f'#{GROUP_HASHTAG} #Raven',
    # 'CRYSTAL': f'#{GROUP_HASHTAG} #Crystal',
}

# Content type hashtags — map your TYPE column values
TYPE_TAGS = {
    'MV':        '#MusicVideo',
    'CONCERT':   '#Concert',
    'VLOG':      '#Vlog',
    'STUDIO':    '#BehindTheScenes',
    'COMEDY':    '#Comedy',
    'NARRATIVE': '#Story',
    'ACTIVITY':  '#Activity',
    'DANCE':     '#Dance',
    'SPORT':     '#Sport',
    'PROMO':     '#NewMusic',
    'EVENT':     '#Event',
    'ART':       '#Art',
}

# Global hashtags added to every post
GLOBAL_TAGS = '#AIMusic #AIPop'

# Platforms to post to (true/false)
PLATFORMS = {
    'Facebook':  False,
    'Twitter/X': True,
    'LinkedIn':  False,
    'GBP':       False,
    'Instagram': True,
    'Pinterest': False,
    'TikTok':    True,
    'Youtube':   False,
    'Threads':   False,
    'Bluesky':   False,
}

# Posting times for N posts/day (add/remove to match --posts-per-day)
POST_TIMES_BY_COUNT = {
    3:  ["09:00:00", "13:00:00", "19:00:00"],
    5:  ["08:00:00", "11:00:00", "14:00:00", "18:00:00", "21:00:00"],
    10: ["07:00:00", "09:00:00", "11:00:00", "13:00:00", "15:00:00",
         "17:00:00", "19:00:00", "20:30:00", "22:00:00", "23:30:00"],
}

# ─────────────────────────────────────────────
# CORE LOGIC (no need to edit below this line)
# ─────────────────────────────────────────────

# All Metricool CSV columns in the correct order
METRICOOL_COLUMNS = [
    'Text','Date','Time','Draft','Facebook','Twitter/X','LinkedIn','GBP','Instagram',
    'Pinterest','TikTok','Youtube','Threads','Bluesky',
    'Picture Url 1','Picture Url 2','Picture Url 3','Picture Url 4','Picture Url 5',
    'Picture Url 6','Picture Url 7','Picture Url 8','Picture Url 9','Picture Url 10',
    'Alt text picture 1','Alt text picture 2','Alt text picture 3','Alt text picture 4',
    'Alt text picture 5','Alt text picture 6','Alt text picture 7','Alt text picture 8',
    'Alt text picture 9','Alt text picture 10',
    'Document title','Shortener','Video Thumbnail Url','Video Cover Frame',
    'Twitter/X Can reply','Twitter/X Type','Twitter/X Poll Duration minutes',
    'Twitter/X Poll Option 1','Twitter/X Poll Option 2','Twitter/X Poll Option 3','Twitter/X Poll Option 4',
    'Pinterest Board','Pinterest Pin Title','Pinterest Pin Link','Pinterest Pin New Format',
    'Instagram Post Type','Instagram Show Reel On Feed',
    'Youtube Video Title','Youtube Video Type','Youtube Video Privacy','Youtube video for kids',
    'Youtube Video Category','Youtube Video Tags','Youtube playlist',
    'GBP Post Type','Facebook Post Type','Facebook Title','First Comment Text',
    'TikTok Title','TikTok disable comments','TikTok disable duet','TikTok disable stitch',
    'TikTok Post Privacy','TikTok Branded Content','TikTok Your Brand','TikTok Auto Add Music',
    'TikTok Photo Cover Index','TikTok musicId','TikTok music title','TikTok music author',
    'TikTok music previewUrl','TikTok music thumbnailUrl','TikTok music soundVolume',
    'TikTok music originalVolume','TikTok music startMillis','TikTok music endMillis',
    'LinkedIn Type','LinkedIn Poll Question','LinkedIn Poll Option 1','LinkedIn Poll Option 2',
    'LinkedIn Poll Option 3','LinkedIn Poll Option 4','LinkedIn Poll Duration',
    'LinkedIn Show link preview','LinkedIn Images as Carousel',
    'Threads Reply Control','Threads Is Spoiler','Threads Post Type','Brand name'
]


def clean_caption(text, official_handle):
    """Strip Sora-platform @handles, keeping the official cross-platform handle."""
    # Keep official handle (strip any dot-suffix like .house)
    text = re.sub(rf'@({re.escape(official_handle)})\.\w*', r'@\1', text)
    # Other @handle.suffix → capitalize base name, drop @
    text = re.sub(r'@(\w+)\.\w*', lambda m: m.group(1).capitalize(), text)
    # Standalone @handle → keep if official, else capitalize and drop @
    text = re.sub(r'@(\w+)', lambda m: f'@{official_handle}' if m.group(1) == official_handle else m.group(1).capitalize(), text)
    return re.sub(r' +', ' ', text).strip()


def load_drive_links(path):
    """Load filename → URL mapping from CSV or XLSX."""
    links = {}
    ext = os.path.splitext(path)[1].lower()
    if ext == '.xlsx':
        import openpyxl
        wb = openpyxl.load_workbook(path)
        for row in wb.active.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                links[row[0]] = row[1]
    else:
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row.get('filename') and row.get('drive_url'):
                    links[row['filename']] = row['drive_url']
    return links


def build_schedule(tracker_path, links_path, start_date, posts_per_day, output_path, seed=42):
    # Load videos, filter out delete candidates
    with open(tracker_path, encoding='utf-8') as f:
        all_rows = list(csv.DictReader(f))
    active = [r for r in all_rows if '[DELETE_CANDIDATE]' not in r.get('notes', '')]
    print(f"Active videos: {len(active)}")

    # Load drive links
    drive_links = load_drive_links(links_path)
    print(f"Drive links loaded: {len(drive_links)}")

    # Shuffle for variety
    random.seed(seed)
    random.shuffle(active)

    # Resolve posting times
    if posts_per_day in POST_TIMES_BY_COUNT:
        post_times = POST_TIMES_BY_COUNT[posts_per_day]
    else:
        # Generate evenly-spaced times across 16 active hours (7am–11pm)
        start_min = 7 * 60
        end_min = 23 * 60 + 30
        step = (end_min - start_min) // (posts_per_day - 1)
        post_times = []
        for i in range(posts_per_day):
            total = start_min + step * i
            post_times.append(f"{total // 60:02d}:{total % 60:02d}:00")

    # Build rows
    output_rows = []
    missing_urls = []
    for i, video in enumerate(active):
        day_offset = i // posts_per_day
        time_slot = i % posts_per_day
        post_date = start_date + timedelta(days=day_offset)

        raw_caption = video.get('caption', '').split('[DELETE_CANDIDATE]')[0].strip()
        caption = clean_caption(raw_caption, OFFICIAL_HANDLE)
        member = video.get('members', 'GROUP')
        ctype = video.get('content_type', '')

        member_tag = MEMBER_TAGS.get(member, f'#{GROUP_HASHTAG}')
        type_tag = TYPE_TAGS.get(ctype, '')
        full_text = f"{caption}\n\n{member_tag} {type_tag} {GLOBAL_TAGS}".strip()

        url = drive_links.get(video.get('new_filename', ''), '')
        if not url:
            missing_urls.append(video.get('new_filename', ''))

        row = {col: '' for col in METRICOOL_COLUMNS}
        row['Text'] = full_text
        row['Date'] = post_date.strftime('%Y-%m-%d')
        row['Time'] = post_times[time_slot]
        row['Draft'] = 'false'
        for platform, enabled in PLATFORMS.items():
            row[platform] = 'true' if enabled else 'false'
        row['Picture Url 1'] = url
        row['Twitter/X Type'] = 'POST'
        row['Instagram Post Type'] = 'REEL'
        row['Instagram Show Reel On Feed'] = 'true'
        row['TikTok disable comments'] = 'false'
        row['TikTok disable duet'] = 'false'
        row['TikTok disable stitch'] = 'false'
        row['TikTok Post Privacy'] = 'PUBLIC_TO_EVERYONE'
        row['TikTok Branded Content'] = 'false'
        row['TikTok Your Brand'] = 'false'
        row['TikTok Auto Add Music'] = 'false'
        output_rows.append(row)

    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=METRICOOL_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)

    end_date = start_date + timedelta(days=len(active) // posts_per_day)
    print(f"\n✓ Written {len(output_rows)} rows to {output_path}")
    print(f"  Schedule: {start_date} → {end_date} ({len(active) // posts_per_day + 1} days)")
    print(f"  Missing Drive URLs: {len(missing_urls)}")
    if missing_urls:
        print("  Missing files:")
        for m in missing_urls[:10]:
            print(f"    {m}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Metricool schedule CSV for Sora creators')
    parser.add_argument('--tracker', required=True, help='Path to master tracker CSV')
    parser.add_argument('--links', required=True, help='Path to DriveLinks CSV or XLSX')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--posts-per-day', type=int, default=10, help='Posts per day (default: 10)')
    parser.add_argument('--output', default='Sora_Metricool_Schedule.csv', help='Output CSV filename')
    args = parser.parse_args()

    build_schedule(
        tracker_path=args.tracker,
        links_path=args.links,
        start_date=date.fromisoformat(args.start),
        posts_per_day=args.posts_per_day,
        output_path=args.output,
    )
