# Auth RestoreCord Control Panel - GUI

## 🎨 Professional GUI Control Panel

A modern, sleek graphical user interface for managing the Auth RestoreCord bot with real-time configuration editing, start/stop controls, and live log monitoring.

![Control Panel](screenshots/control_panel_preview.png)

## ✨ Features

### 🎯 Real-Time Control
- **Start/Stop Bot** - Control the bot with clickable buttons
- **Live Status Indicator** - Visual status (Running/Stopped)
- **Non-Blocking Operations** - Edit config while bot runs

### ⚙️ Configuration Editor
- **Click-to-Edit Fields** - All settings in one place
- **Organized Sections** - Grouped by category
- **Save & Apply** - Changes apply instantly
- **Auto-Reload** - Refresh config from file

### 📊 Live Log Viewer
- **Real-Time Logs** - See bot activity as it happens
- **Color-Coded Messages** - Info, Warning, Error, Success
- **Side Panel Layout** - Logs don't interfere with controls
- **Clear Function** - Clean up old logs

### 🎨 Professional Design
- **Black and White Theme** - Pure monochrome aesthetic inspired by underground/doxbin style
- **Monochrome Palette** - Pure blacks and whites with grey accents for maximum contrast
- **Monospace Font** - Courier New for that terminal/hacker aesthetic
- **ASCII Art** - Super detailed crypto anarchist cat with Bitcoin symbols
- **ASCII Elements** - Decorative brackets and symbols throughout
- **Clean Experience** - Minimalist, edgy design with no color distractions

## 🚀 Usage

### Launch the Control Panel

```bash
python3 auth_control_panel.py
```

Or double-click the file if your system supports it.

### Configuration Sections

The control panel organizes settings into logical groups:

#### 1. Discord Configuration
- **Token** - Your Discord user token (password protected)
- **Guild ID** - Server ID
- **User ID** - Your user ID
- **Bot Client ID** - For OAuth2

#### 2. RestoreCord Settings
- **URL** - RestoreCord API endpoint
- **Server ID** - RestoreCord server
- **API Key** - Optional API key

#### 3. Message Forwarding Configuration
- **Source Channel ID** - Channel where template messages are stored
- **Auth Message ID** - ID of message to forward for verification
- **Additional Text** - Extra text to send with forwarded message

#### 4. Application Requirements
- **Require Add People** - Enable/disable people requirement
- **Required Count** - How many people to add

#### 5. Server Configuration
- **Main Server Invite** - Link for added users

#### 6. Timing Settings
- **Channel Creation Wait** - Delay for channel creation
- **Auth Check Interval** - How often to check status

### How to Use

1. **Launch** - Run `python3 auth_control_panel.py`
2. **Edit Config** - Click any field and type new values
3. **Save** - Click "[ 💾 SAVE ]" to apply changes
4. **Start Bot** - Click "[ ▶ START ]" to begin monitoring
5. **Watch Logs** - View real-time activity in the right panel
6. **Stop Bot** - Click "■ STOP BOT" when done

### While Running

- ✅ Edit config anytime (bot keeps running)
- ✅ Logs update in real-time
- ✅ Status indicator shows current state
- ✅ Click "⟳ RELOAD" to refresh from file
- ✅ Click "🗑 CLEAR" to clear old logs

## 🎨 Color Scheme

The control panel uses a pure black and white monochrome palette:

- **Background**: Pure blacks (#000000, #0a0a0a, #1a1a1a)
- **Primary Accent**: Pure White (#ffffff)
- **Secondary Accent**: Light Grey (#cccccc)
- **Text**: White and grey tones (#ffffff, #b0b0b0, #666666)
- **Buttons**: White on black for maximum contrast

## 📋 Requirements

```bash
# Python 3.6+
# tkinter (usually included with Python)

# Install if needed:
sudo apt-get install python3-tk  # Ubuntu/Debian
brew install python-tk@3.9       # macOS
```

## 🖥️ Layout

```
┌─────────────────────────────────────────────────────────────┐
│                   _.._                                       │
│                 .'    '.                                     │
│                /   __   \                                    │
│               |   /  \   |                                   │
│               |   \__/   |     ₿  Ξ                         │
│              /\          /\                                  │
│             /  '.______.'  \                                 │
│            /    /|    |\    \                                │
│           |    | |    | |    |                               │
│           |    |_|    |_|    |                               │
│           |   /   \  /   \   |                               │
│           |  /     \/     \  |                               │
│          /__/      ||      \__\                              │
│         /   \      ||      /   \                             │
│        /     \     ||     /     \                            │
│       /  ⚡   \    ||    /  ₿   \                           │
│      /__      \   ||   /      __\                            │
│         \_    /\  ||  /\    _/                               │
│           \__/  \_||_/  \__/                                 │
│                 crypto anarchist                             │
│                                                              │
│           ◈ Auth RestoreCord Control ◈                      │
│       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━               │
│       [ Real-time Configuration & Monitoring ]               │
│       ▲ crypto secured ▲                                     │
├──────────────────────────────────┬──────────────────────────┤
│                                  │                          │
│  [ BOT CONTROLS ]                │   [ LIVE LOGS ]          │
│  >> Status: ◆ OFFLINE            │                          │
│  [▶ START] [■ STOP] [⟳ RELOAD]  │   [12:34:56] Started...  │
│                                  │   [12:34:57] Checking... │
│  [ CONFIGURATION ]               │   [12:34:58] User...     │
│  [💾 SAVE]                       │   [12:34:59] Approved... │
│                                  │                          │
│  >> Discord Configuration        │   [12:35:00] Logs...     │
│    Token: ●●●●●●●●●●●           │   [12:35:01] Continue... │
│    ...                           │   [12:35:02] Running...  │
│                                  │                          │
│  >> Message Forwarding Config    │   [🗑 CLEAR]             │
│    Source Channel ID: ...        │                          │
│    ...                           │                          │
│                                  │                          │
└──────────────────────────────────┴──────────────────────────┘
```

## 🔧 Technical Details

### Architecture

- **GUI Framework**: tkinter (Python's built-in GUI toolkit)
- **Threading**: Separate thread for bot monitoring
- **Logging**: Queue-based log forwarding to GUI
- **Config**: Direct file editing with hot-reload

### Features

- **Non-blocking**: Bot runs in background thread
- **Real-time**: Logs update via queue every 100ms
- **Thread-safe**: Proper locking for config access
- **Error handling**: Try-catch blocks with user feedback
- **Clean shutdown**: Proper thread termination

### File Structure

```
auth_control_panel.py          # Main GUI application
auth_restorecore_main.py       # Bot logic (imported)
auth_restorecore_config.py     # Config file (edited)
```

## 🎯 Use Cases

### Perfect For:

- **Quick Setup** - Visual config is easier than editing files
- **Monitoring** - Watch bot activity in real-time
- **Testing** - Start/stop quickly while developing
- **Management** - Control multiple settings in one place
- **Live Operations** - Adjust config without restarting

### Not Needed For:

- **Headless Servers** - Use command-line version instead
- **Automated Deployment** - Use environment variables
- **CI/CD** - Stick with programmatic configuration

## 🐛 Troubleshooting

### GUI Won't Start

```bash
# Install tkinter
sudo apt-get install python3-tk

# Check if working
python3 -c "import tkinter; print('OK')"
```

### Config Not Saving

- Check file permissions on `auth_restorecore_config.py`
- Make sure no syntax errors in config file
- Try "⟳ RELOAD" to refresh

### Logs Not Updating

- Make sure bot is started (click "▶ START BOT")
- Check that `auth_restorecore_main.py` is present
- Verify logger is configured in bot module

## 📝 License

Same as the main Auth RestoreCord project.

## 🙏 Credits

Built with Python's tkinter for cross-platform compatibility.
Design inspired by modern development tools and IDEs.
