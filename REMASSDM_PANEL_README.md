# Re-Mass DM Control Panel

## 🎨 Professional GUI Control Panel for Re-Mass DM

A modern, sleek graphical user interface for managing the Re-Mass DM bot without requiring Discord server context. Perfect for re-DMing users from bot DM history.

## Why Use the Panel?

The panel interface solves a key problem with the original `remassdm.py`:
- **No Server Required**: Since re-mass DM uses bot DM history (not server members), you don't need to be in a Discord server
- **Easier Management**: Visual interface for token management and operation control
- **Live Monitoring**: See real-time logs and status updates
- **Better Control**: Start/stop operations with a click

## ✨ Features

### 🎯 Real-Time Control
- **Start/Stop Operation** - Control re-mass DM with clickable buttons
- **Live Status Indicator** - Visual status (Idle/Running/Stopping)
- **Non-Blocking UI** - Edit configuration while operation runs

### ⚙️ Configuration Management
- **Token Management** - Add/edit bot tokens visually
- **Message Editor** - Type your re-DM message
- **Paste Mode** - Paste previous DM logs to retry with same bot-user pairings ✨NEW
- **Timing Controls** - Adjust DM delays
- **No Files to Edit** - Everything in the GUI

### 📝 Paste Mode (NEW Feature)
- **Paste DM Logs** - Copy/paste logs from previous DM operations
- **Strict Bot-User Pairing** - Each bot only DMs users it previously DMed
- **Auto-Matching** - System automatically matches bot names to tokens
- **Safe Skipping** - Bots without tokens are skipped (not redistributed)
- **See:** [PASTE_MODE_README.md](PASTE_MODE_README.md) for detailed guide

### 📊 Live Log Viewer
- **Real-Time Logs** - See bot activity as it happens
- **Color-Coded Messages** - Info, Warning, Error, Success
- **Clear Function** - Clean up old logs
- **Scrollable View** - Review operation history

### 🎨 Professional Design
- **Black and White Theme** - Clean monochrome aesthetic
- **Monospace Font** - Terminal/hacker style
- **ASCII Art Header** - Decorative design elements
- **Intuitive Layout** - Everything you need in one window

## 🚀 Quick Start

### 1. Launch the Panel

**Option A: Using the launch script**
```bash
./launch_remassdm_panel.sh
```

**Option B: Direct Python**
```bash
python3 remassdm_panel.py
```

### 2. Configure Tokens

In the "Bot Tokens" section:
1. Add your Discord bot tokens (one per line)
2. First token = controller bot (optional, can skip)
3. Rest = sender bots that will DM users
4. Need at least 2 tokens minimum

Example:
```
MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIjKl.MnOpQrStUvWxYz1234567890
OTg3NjU0MzIxMDk4NzY1NDMy.LmNoPq.RsTuVwXyZ0987654321abcd
```

### 3. Enter Your Message

In the "Message to Send" section:
- Type the message you want to send
- Note: The actual embed content is hardcoded
- This field is for reference/future use

### 4. Adjust Timing (Optional)

- **DM Delay**: Time between each DM (default: 0.10 seconds)
- Lower = faster but riskier
- Higher = slower but safer

### 5. Start Operation

1. Click **"▶ START RE-MASS DM"**
2. Watch the logs for progress
3. Status indicator shows "◆ RUNNING"
4. Operation runs automatically

### 6. Monitor Progress

The log viewer shows:
- Scanning phase: Finding users from DM history
- Total users found
- Re-DM phase: Sending messages
- Success/failure for each user
- Bot status and warnings

### 7. Stop if Needed

- Click **"■ STOP"** to halt the operation
- Bots will finish current DM and stop gracefully

## 🖥️ Panel Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   ◈ Re-Mass DM Control Panel ◈          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  [ Re-DM Users from Bot DM History ]

├──────────────────────────────────┬──────────────────────────┤
│                                  │                          │
│  [ OPERATION CONTROL ]           │   [ LIVE LOGS ]          │
│  >> Status: ◆ IDLE               │                          │
│  [▶ START] [■ STOP]              │   [12:34:56] Started...  │
│                                  │   [12:34:57] Scanning... │
│  [ CONFIGURATION ]               │   [12:34:58] Found 150...|
│                                  │   [12:34:59] Re-DMing... │
│  >> Bot Tokens                   │   [12:35:00] Success...  │
│    [Text area with tokens]       │   [12:35:01] Complete!   │
│                                  │                          │
│  >> Message to Send              │   [🗑 CLEAR LOGS]        │
│    [Text area for message]       │                          │
│                                  │                          │
│  >> Timing Configuration         │                          │
│    DM Delay: 0.10                │                          │
│                                  │                          │
└──────────────────────────────────┴──────────────────────────┘
```

## 📋 Requirements

```bash
# Python 3.6+
# tkinter (usually included with Python)
# discord.py

# Install if needed:
pip3 install discord.py

# tkinter:
sudo apt-get install python3-tk  # Ubuntu/Debian
brew install python-tk@3.9       # macOS
```

## 🎯 Use Cases

### Perfect For:

- **Standalone Operation** - No Discord server needed
- **Visual Management** - Easier than command-line
- **Testing** - Start/stop quickly while developing
- **Monitoring** - Watch bot activity in real-time
- **Token Management** - Swap tokens without editing files

### Advantages Over Command Version:

| Feature | remassdm.py | Panel |
|---------|-------------|-------|
| **Server Required** | Yes (for commands) | No |
| **Token Management** | Edit file | Visual editor |
| **Live Logs** | Console only | GUI viewer |
| **Start/Stop** | Commands | Buttons |
| **Status** | Console output | Visual indicator |

## 🔧 Technical Details

### How It Works

1. **Scanning Phase**:
   - Logs in each bot token
   - Scans `private_channels` for existing DMs
   - Collects unique user IDs across all bots

2. **Re-DM Phase**:
   - Distributes users across available bots
   - Each bot processes its assigned users
   - Sends DMs with rate limiting
   - Handles errors and dead bots

3. **Thread Architecture**:
   - GUI runs on main thread
   - Operation runs on background thread
   - Async event loop for Discord operations
   - Queue-based logging to GUI

### File Structure

```
remassdm_panel.py              # Main GUI application
launch_remassdm_panel.sh       # Launch script
REMASSDM_PANEL_README.md       # This file
```

## 🐛 Troubleshooting

### Panel Won't Start

```bash
# Check Python installation
python3 --version

# Check tkinter
python3 -c "import tkinter; print('OK')"

# Install tkinter if missing
sudo apt-get install python3-tk  # Ubuntu/Debian
```

### Discord.py Errors

```bash
# Install/update discord.py
pip3 install --upgrade discord.py
```

### "No existing DM channels found"

- Bots haven't DMed anyone yet
- DM history not cached by Discord
- Try running `embeddm.py` first to establish DM history

### Bots Get Flagged

- Discord detected spam behavior
- Increase DM delay (try 0.20 or higher)
- Use fewer bots simultaneously
- Take breaks between operations

### Logs Not Updating

- Make sure operation is started
- Check that tokens are valid
- Verify internet connection

## 🎨 Customization

### Change DM Delay

Default: 0.10 seconds

- Lower (0.05): Faster, riskier
- Higher (0.20): Slower, safer
- Recommended: 0.10 to 0.15

### Modify Embed Content

To change the embed message/image:
1. Open `remassdm_panel.py`
2. Find the `send_dm_to_user` function
3. Edit the `embed` variable
4. Save and restart panel

## 📊 Operation Flow

```
1. User adds tokens and message
2. User clicks START
   ↓
3. Panel logs in all bot tokens
   ↓
4. SCANNING PHASE
   - Each bot scans private_channels
   - Collects user IDs
   - Shows count in logs
   ↓
5. RE-DM PHASE
   - Distributes users across bots
   - Each bot DMs its assigned users
   - Shows progress in logs
   ↓
6. COMPLETION
   - Shows final statistics
   - Logs saved to remassdm.txt
   - Operation complete
```

## 🔒 Security Notes

- **Token Safety**: Tokens are only stored in memory during operation
- **No File Storage**: Tokens are not saved to disk by the panel
- **Private**: All operations happen locally
- **Secure**: Uses Discord's official API

## 📝 Comparison with Original

### remassdm.py (Command Version)
- Requires Discord server context
- Uses `!remassdm` command
- Console-based
- Edit file for tokens

### remassdm_panel.py (Panel Version)
- No server required
- GUI buttons
- Visual logs
- Edit tokens in UI

**Both versions do the same thing**, just different interfaces!

## 🙏 Credits

Built on top of `remassdm.py` with a tkinter GUI inspired by the auth control panel design.

## 📄 License

Same as the main COOL project.

---

**Quick Command Reference**

```bash
# Launch panel
./launch_remassdm_panel.sh

# Or directly
python3 remassdm_panel.py

# Check requirements
python3 -c "import tkinter, discord; print('All good!')"
```

**Need help?** Check the logs in the panel or see `REMASSDM_README.md` for more info.
