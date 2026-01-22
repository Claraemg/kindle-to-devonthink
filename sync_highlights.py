#!/usr/bin/env python3
"""
Kindle to DEVONthink Highlight Sync

Parses My Clippings.txt from a Kindle and imports Markdown notes
directly into DEVONthink. One note per book, sorted by page number.

Author: Clara (with help from Claude)
License: MIT
"""

import re
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


# === CONFIGURATION ===

STATE_FILE = Path.home() / ".kindle-sync-state.json"
LOG_FILE = Path.home() / ".kindle-sync.log"
DEVONTHINK_GROUP = "Kindle Highlights"  # Group name in DEVONthink


# === DATA STRUCTURES ===

@dataclass
class Highlight:
    """A single highlight or note from a book."""
    text: str
    page: Optional[int] = None
    location_start: Optional[int] = None
    location_end: Optional[int] = None
    date_added: Optional[datetime] = None
    is_note: bool = False
    highlight_id: str = ""

    def __post_init__(self):
        content = f"{self.text}{self.page}{self.location_start}"
        self.highlight_id = hashlib.md5(content.encode()).hexdigest()[:12]

    @property
    def sort_key(self):
        return (
            self.page if self.page is not None else 999999,
            self.location_start if self.location_start is not None else 999999,
            self.date_added or datetime.min
        )


@dataclass
class Book:
    """A book with its highlights."""
    title: str
    author: str = "Unknown"
    highlights: list = field(default_factory=list)

    @property
    def safe_filename(self) -> str:
        title = re.sub(r'[<>:"/\\|?*]', '', self.title)
        author = re.sub(r'[<>:"/\\|?*]', '', self.author)
        if author and author != "Unknown":
            return f"{title} — {author}"
        return title


# === PARSING ===

def parse_clippings(clippings_path: Path) -> dict[str, Book]:
    """Parse My Clippings.txt and return a dictionary of books."""
    books = {}

    if not clippings_path.exists():
        logging.error(f"Clippings file not found: {clippings_path}")
        return books

    content = clippings_path.read_text(encoding='utf-8-sig')
    entries = content.split('==========')

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue

        lines = entry.split('\n')
        if len(lines) < 3:
            continue

        title_line = lines[0].strip()
        title, author = parse_title_author(title_line)

        meta_line = lines[1].strip()
        highlight_meta = parse_metadata(meta_line)

        if highlight_meta is None:
            continue

        text = '\n'.join(lines[3:]).strip()
        if not text:
            continue

        book_key = f"{title}|{author}"
        if book_key not in books:
            books[book_key] = Book(title=title, author=author)

        highlight = Highlight(
            text=text,
            page=highlight_meta.get('page'),
            location_start=highlight_meta.get('location_start'),
            location_end=highlight_meta.get('location_end'),
            date_added=highlight_meta.get('date'),
            is_note=highlight_meta.get('is_note', False)
        )

        books[book_key].highlights.append(highlight)

    return books


def parse_title_author(line: str) -> tuple[str, str]:
    match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', line)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return line.strip(), "Unknown"


def parse_metadata(line: str) -> Optional[dict]:
    if not line.startswith('-'):
        return None

    result = {
        'page': None,
        'location_start': None,
        'location_end': None,
        'date': None,
        'is_note': False
    }

    result['is_note'] = 'Your Note' in line or 'Your Bookmark' in line

    page_match = re.search(r'page\s+(\d+)', line, re.IGNORECASE)
    if page_match:
        result['page'] = int(page_match.group(1))

    loc_match = re.search(r'location\s+(\d+)(?:-(\d+))?', line, re.IGNORECASE)
    if loc_match:
        result['location_start'] = int(loc_match.group(1))
        if loc_match.group(2):
            result['location_end'] = int(loc_match.group(2))

    date_match = re.search(r'Added on\s+(.+)$', line, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    return result


def parse_date(date_str: str) -> Optional[datetime]:
    formats = [
        "%A, %d %B %Y %H:%M:%S",
        "%A, %B %d, %Y %H:%M:%S",
        "%A, %B %d, %Y, %H:%M:%S",
        "%A %d %B %Y %H:%M:%S",
        "%d %B %Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


# === STATE MANAGEMENT ===

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            logging.warning("Corrupt state file, starting fresh")
    return {"imported_ids": []}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# === DEVONTHINK INTEGRATION ===

def import_to_devonthink(name: str, content: str, output_dir: Path) -> bool:
    """Write a Markdown document to the output folder for DEVONthink to index."""

    output_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = re.sub(r'[<>:"/\\|?*]', '', name) + '.md'
    filepath = output_dir / safe_filename

    try:
        filepath.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        logging.error(f"Error writing file: {e}")
        return False


# === MARKDOWN GENERATION ===

def generate_markdown(book: Book, existing_ids: set) -> tuple[str, list[str]]:
    sorted_highlights = sorted(book.highlights, key=lambda h: h.sort_key)
    new_highlights = [h for h in sorted_highlights if h.highlight_id not in existing_ids]

    if not new_highlights and existing_ids:
        return None, []

    lines = [
        f"# {book.title}",
        f"## By {book.author}",
        "",
        "---",
        "### Highlights",
        "",
    ]

    for highlight in sorted_highlights:
        # Build the highlight text as a blockquote
        if highlight.is_note:
            lines.append(f"> *[Note]* {highlight.text}")
        else:
            lines.append(f"> {highlight.text}")
        lines.append("")

        # Build metadata line with colors
        meta_parts = []
        if highlight.page:
            meta_parts.append(f'<font color="#d97706"><b>Page {highlight.page}</b></font>')
        if highlight.location_start:
            if highlight.location_end and highlight.location_end != highlight.location_start:
                meta_parts.append(f'<font color="#2563eb"><b>Loc {highlight.location_start}-{highlight.location_end}</b></font>')
            else:
                meta_parts.append(f'<font color="#2563eb"><b>Loc {highlight.location_start}</b></font>')
        if highlight.date_added:
            date_str = highlight.date_added.strftime("%A, %d %B %Y %H:%M:%S")
            meta_parts.append(f'<font color="#059669">{date_str}</font>')

        if meta_parts:
            lines.append(f'<p><small>{" &bull; ".join(meta_parts)}</small></p>')
        lines.append("")
        lines.append("---")
        lines.append("")

    new_ids = [h.highlight_id for h in new_highlights]
    return '\n'.join(lines), new_ids


def process_book(book: Book, state: dict, output_dir: Path) -> int:
    """Generate markdown and write to output folder."""
    existing_ids = set(state.get("imported_ids", []))

    markdown, new_ids = generate_markdown(book, existing_ids)

    if markdown is None:
        logging.info(f"No new highlights for: {book.title}")
        return 0

    if import_to_devonthink(book.safe_filename, markdown, output_dir):
        state["imported_ids"].extend(new_ids)
        logging.info(f"Saved: {book.safe_filename} (+{len(new_ids)} highlights)")
        return len(new_ids)
    else:
        logging.error(f"Failed to save: {book.safe_filename}")
        return 0


# === MAIN ===

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def find_clippings() -> Optional[Path]:
    """Find My Clippings.txt on mounted Kindle."""
    for name in ["Kindle", "KINDLE", "kindle"]:
        kindle = Path(f"/Volumes/{name}")
        if kindle.exists():
            for loc in ["documents/My Clippings.txt", "My Clippings.txt"]:
                clippings = kindle / loc
                if clippings.exists():
                    logging.info(f"Found Kindle at: {kindle}")
                    return clippings

    logging.error("Kindle not found or My Clippings.txt missing")
    return None


def main():
    setup_logging()
    logging.info("=" * 50)
    logging.info("Kindle highlight sync started")

    clippings_path = find_clippings()
    if not clippings_path:
        return 1

    state = load_state()
    logging.info(f"Loaded state: {len(state.get('imported_ids', []))} highlights already imported")

    books = parse_clippings(clippings_path)
    logging.info(f"Found {len(books)} books with highlights")

    output_dir = Path.home() / "Documents" / "Kindle Highlights"

    total_new = 0
    for book in books.values():
        total_new += process_book(book, state, output_dir)

    save_state(state)
    logging.info(f"Sync complete: {total_new} new highlights saved to {output_dir}")
    logging.info("=" * 50)

    return 0


if __name__ == "__main__":
    exit(main())
