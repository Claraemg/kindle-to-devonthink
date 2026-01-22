# Kindle to DEVONthink

Automatically sync your Kindle highlights directly into DEVONthink.

## What it does

1. Plug in your Kindle
2. Highlights import automatically into DEVONthink
3. One Markdown document per book, in a "Kindle Highlights" group

No subscriptions, no cloud services, no Amazon login required.

## Requirements

- macOS 12+
- Python 3.8+ (included on modern Macs)
- DEVONthink 3
- An older Kindle that mounts as a USB drive (pre-2018 models like Paperwhite 1-3)

## Installation

```bash
git clone https://github.com/Claraemg/kindle-to-devonthink.git
cd kindle-to-devonthink
bash install.sh
```

That's it. DEVONthink will be set up automatically.

## Output format

Each book becomes a Markdown document in DEVONthink with YAML frontmatter:

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

Highlights import automatically when you plug in your Kindle. To run manually:

```bash
python3 ~/.kindle-sync/sync_highlights.py
```

Check the log:
```bash
cat ~/.kindle-sync.log
```

## Where do the highlights go?

They're imported into a group called "Kindle Highlights" in your DEVONthink inbox. You can move them to any database afterward.

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
