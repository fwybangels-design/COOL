# Re-Mass DM Tool - Usage Guide

## Quick Overview

The Re-Mass DM tool has **TWO** ways to use it:

### 1. Panel Interface (RECOMMENDED - No Server Needed!) ⭐

**Perfect for:** Starting operations without being in a Discord server

```bash
# Launch the panel
./launch_remassdm_panel.sh

# OR
python3 remassdm_panel.py
```

**Features:**
- ✅ No Discord server required
- ✅ Visual token management
- ✅ Live logs and monitoring
- ✅ Start/stop with buttons
- ✅ Easy to use

**See:** `REMASSDM_PANEL_README.md` for full documentation

---

### 2. Command-Line Version (Original)

**Perfect for:** When you're already in a Discord server and want to use commands

```bash
# Run the bot
python3 remassdm.py

# In Discord, use:
!remassdm your message here
!remassdme  # Emergency stop
```

**Features:**
- ✅ Discord command interface
- ✅ Integrated with server
- ✅ Command-line based

**See:** `REMASSDM_README.md` for full documentation

---

## Which One Should I Use?

### Use the **Panel** if:
- You want to start operations quickly
- You don't need Discord server integration
- You prefer visual interfaces
- You want easier token management

### Use the **Command Version** if:
- You're already running bots in Discord
- You prefer command-line tools
- You want server integration
- You're comfortable editing Python files

## Both Do the Same Thing!

Both versions:
1. Scan bot tokens for existing DM channels
2. Find users the bots have previously contacted
3. Re-DM those users with your message
4. Log everything to a file

The only difference is **how you control it**:
- **Panel**: GUI with buttons
- **Command**: Discord commands

---

## Quick Start Comparison

| Action | Panel | Command |
|--------|-------|---------|
| **Setup** | Add tokens in GUI | Edit TOKENS in .py file |
| **Start** | Click "START" button | Type `!remassdm message` |
| **Stop** | Click "STOP" button | Type `!remassdme` |
| **Logs** | See in GUI | See in console |
| **Status** | Visual indicator | Console output |

---

## Files Reference

- `remassdm_panel.py` - Panel interface (GUI)
- `remassdm.py` - Command interface (Discord bot)
- `REMASSDM_PANEL_README.md` - Panel documentation
- `REMASSDM_README.md` - Command documentation
- `launch_remassdm_panel.sh` - Panel launch script
- `QUICK_START.md` - Command quick start
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

## Need Help?

**For Panel:** See `REMASSDM_PANEL_README.md`
**For Command:** See `REMASSDM_README.md`
**For Technical Details:** See `IMPLEMENTATION_SUMMARY.md`

---

## Why Panel is Better for This Use Case

The re-mass DM tool **doesn't need a Discord server** because:
- It uses bot DM history (not server members)
- It scans `private_channels` (not guild members)
- It operates independently

So a **panel interface makes more sense** than requiring server commands!

---

**TL;DR:** Use `remassdm_panel.py` for easy standalone operation! 🎯
