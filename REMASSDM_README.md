# Re-Mass DM Tool (remassdm.py)

## Overview
This tool scans bot tokens to find users that the bots have previously DMed and allows you to re-DM them with a new message.

## How It Works
1. **Scanning Phase**: The tool scans all bot tokens and retrieves their existing DM channels to identify users they've previously contacted
2. **Re-DM Phase**: Distributes the found users across available bots and re-sends DMs to them

## Setup
1. Use the same bot tokens as in `embeddm.py` - edit the `TOKENS` list in `remassdm.py`
2. First token is the controller bot (the one you'll issue commands with)
3. Remaining tokens are sender bots that will perform the re-mass DM

## Usage
1. Run the bot:
   ```bash
   python3 remassdm.py
   ```

2. In any Discord channel where the controller bot is present, use:
   ```
   !remassdm <your message here>
   ```

3. Emergency stop (if needed):
   ```
   !remassdme
   ```

## Features
- **Automatic Scanning**: Finds all users the bots have previously DMed
- **Distributed Re-DMing**: Spreads the workload across multiple bot tokens
- **Progress Tracking**: Real-time status updates in Discord
- **Logging**: Saves detailed logs to `remassdm.txt`
- **Dead Bot Detection**: Automatically detects and marks bots that get flagged/disabled
- **Rate Limit Protection**: Built-in delays to avoid hitting Discord rate limits

## Configuration
Edit these values in the `DELAY CONFIGURATION` section:

- `STATUS_UPDATE_INTERVAL`: How often status updates (default: 5.0 seconds)
- `DM_DELAY`: Delay between each DM per bot (default: 0.10 seconds)

## Important Notes
- This tool only re-DMs users that the bots have **already contacted before**
- It does NOT DM new users - use `embeddm.py` for that
- The bot tokens need to have their DM channels cached (Discord keeps recent DM channels)
- Mass-DMing may violate Discord Terms of Service - use responsibly

## Differences from embeddm.py
- **remassdm.py**: Re-DMs users the bots have already contacted
- **embeddm.py**: DMs all members in a server

## Output Files
- `remassdm.txt`: Detailed log of the re-mass DM operation including:
  - Users found per bot
  - Success/failure status for each DM
  - Total statistics
  - Bot status and warnings
