# Kindle to DEVONthink

Automatically sync your Kindle highlights to DEVONthink as Markdown notes.

## What it does

1. Plug in your Kindle
2. Highlights sync automatically
3. One Markdown file per book appears in DEVONthink

No subscriptions, no cloud services, no Amazon login required.

## Requirements

- macOS 12+
- Python 3.8+ (included on modern Macs)
- DEVONthink (any version)
- An older Kindle that mounts as a USB drive (pre-2018 models like Paperwhite 1-3)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/kindle-to-devonthink.git
cd kindle-to-devonthink
./install.sh
```

Then point DEVONthink at the highlights folder:
1. Open DEVONthink
2. **File > Index Files and Folders...**
3. Select `~/Documents/Kindle Highlights/`

## Output format

Each book becomes a Markdown file with YAML frontmatter:

```markdown
---
title: "Howards End"
author: "E. M. Forster"
synced: 2025-01-12
---

## Highlights

- **p. 14** — "Only connect! That was the whole of her sermon."

- **p. 72** — *[Note]* This connects to Williams on structures of feeling.
```

See `example-output.md` for a full example.

## Usage

Highlights sync automatically when you plug in your Kindle. To run manually:

```bash
python3 ~/.kindle-sync/sync_highlights.py
```

Check the log:
```bash
cat ~/.kindle-sync.log
```

## How it handles duplicates

Each highlight gets a unique ID based on its content. Syncing multiple times only adds new highlights, never duplicates.

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.user.kindle-sync.plist
rm -rf ~/.kindle-sync
rm ~/Library/LaunchAgents/com.user.kindle-sync.plist
rm ~/.kindle-sync-state.json
rm ~/.kindle-sync.log
```

## License

MIT
