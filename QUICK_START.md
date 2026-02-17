# Quick Start Guide - remassdm.py

## What is this?
A tool that scans your bot tokens and re-DMs users they've previously contacted.

## Quick Setup (3 steps)

### 1. Add Your Tokens
Edit `remassdm.py` and add your Discord bot tokens:
```python
TOKENS = [
    "YOUR_CONTROLLER_TOKEN_HERE",  # First token = controller bot
    "YOUR_SENDER_TOKEN_1_HERE",    # Rest = sender bots
    "YOUR_SENDER_TOKEN_2_HERE",
    # Add more as needed
]
```

### 2. Run the Bot
```bash
python3 remassdm.py
```

### 3. Use in Discord
In any channel where your controller bot is present:
```
!remassdm Hey everyone! New message here!
```

## Commands

| Command | Description |
|---------|-------------|
| `!remassdm <message>` | Start re-DMing users the bots have contacted before |
| `!remassdme` | Emergency stop |

## What Happens

1. **Scanning**: Bot scans all sender tokens for existing DM channels
2. **Found**: Shows how many users were found across all bots
3. **Re-DMing**: Distributes users across bots and sends DMs
4. **Complete**: Shows statistics and saves log to `remassdm.txt`

## Important Notes

⚠️ **Only re-DMs users the bots have ALREADY contacted**
- Will NOT DM new users
- For new users, use `embeddm.py` instead

⚠️ **Discord Limitations**
- Only scans cached DM channels (recent conversations)
- Old DMs may not appear if not cached

⚠️ **Rate Limits**
- Default delay: 0.1 seconds between DMs per bot
- Adjust `DM_DELAY` in code if needed

## Troubleshooting

**"No existing DM channels found!"**
- Bots haven't DMed anyone yet, or DMs not cached
- Run `embeddm.py` first to DM users

**"No available sender bots!"**
- Check your tokens are valid
- Make sure tokens are not empty strings

**Bot gets flagged/disabled**
- Discord detected spam behavior
- Try increasing `DM_DELAY` for slower sending
- Use fewer concurrent bots

## Files Created

- `remassdm.txt` - Detailed log of operation

## Need More Help?

- See `REMASSDM_README.md` for full documentation
- See `IMPLEMENTATION_SUMMARY.md` for technical details
- See `SECURITY_SUMMARY.md` for security information
