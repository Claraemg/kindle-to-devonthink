# Kindle to DEVONthink

Automatically sync your Kindle highlights directly into DEVONthink.

## What it does

1. Plug in your Kindle
2. Highlights are parsed and saved as Markdown files
3. One Markdown document per book, sorted by page number

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

This installs the sync script and a LaunchAgent that runs when you plug in your Kindle.

**Note:** You may need to grant Terminal (or your terminal app) Full Disk Access in **System Settings → Privacy & Security → Full Disk Access** for the script to read your Kindle.

## Setting up automatic DEVONthink import (optional)

By default, highlights are saved to `~/Documents/Kindle Highlights/`. To have them automatically import into DEVONthink:

1. Open **Finder** and navigate to **Documents → Kindle Highlights**
2. Right-click the **Kindle Highlights** folder
3. Click **Services → Folder Actions Setup**
4. Click the **+** button
5. Navigate to: `~/Library/Scripts/Folder Action Scripts/`
6. Select **"DEVONthink - Import & Delete.scpt"**
7. Click **Attach**

If the script isn't there, install it via DEVONthink: **Help → Support Assistant → Install Extras**.

Now when you plug in your Kindle, highlights will automatically appear in DEVONthink's inbox. DEVONthink must be running for this to work.

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

Highlights are saved to `~/Documents/Kindle Highlights/` as Markdown files. If you set up the Folder Action, they'll automatically import to DEVONthink's inbox and the originals will be deleted. Otherwise, drag the files into DEVONthink manually.

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
