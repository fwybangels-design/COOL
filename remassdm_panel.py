#!/usr/bin/env python3
"""
Re-Mass DM Control Panel - GUI
Control panel for managing the Re-Mass DM bot with token configuration, message input, and live monitoring.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import logging
import sys
import time
from datetime import datetime
import asyncio
import discord

# Import remassdm module functions
sys.path.insert(0, '/home/runner/work/COOL/COOL')


class ColorScheme:
    """Color scheme for the control panel - Black and white aesthetic."""
    BG_DARK = "#000000"          # Pure black
    BG_MEDIUM = "#0a0a0a"        # Nearly black
    BG_LIGHT = "#1a1a1a"         # Dark grey
    ACCENT_PRIMARY = "#ffffff"   # Pure white
    ACCENT_SECONDARY = "#cccccc" # Light grey
    TEXT_PRIMARY = "#ffffff"     # Pure white
    TEXT_SECONDARY = "#b0b0b0"   # Medium grey
    TEXT_MUTED = "#666666"       # Dark grey
    BTN_PRIMARY = "#ffffff"      # White
    HOVER_LIGHT = "#e0e0e0"      # Light hover


class LogHandler(logging.Handler):
    """Custom logging handler that sends logs to a queue for GUI display."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)


class RemassDMPanel:
    """Re-Mass DM control panel GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("◈ Re-Mass DM Control ◈")
        self.root.geometry("1200x800")
        self.root.configure(bg=ColorScheme.BG_DARK)
        
        # Set minimum size
        self.root.minsize(1000, 600)
        
        # Operation state
        self.operation_running = False
        self.operation_thread = None
        self.log_queue = queue.Queue()
        
        # Discord clients
        self.sender_clients = []
        self.sender_meta = {}
        
        # Configuration
        self.tokens = []
        self.message_text = ""
        
        # Setup logging
        self.setup_logging()
        
        # Create UI
        self.create_ui()
        
        # Start log update loop
        self.update_logs()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_logging(self):
        """Setup logging to capture logs in the GUI."""
        self.logger = logging.getLogger("RemassD M")
        self.logger.setLevel(logging.INFO)
        
        # Add handler to send logs to GUI
        handler = LogHandler(self.log_queue)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(handler)
        
        # Also log to console
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(console)
    
    def create_ui(self):
        """Create the main UI layout."""
        # Main container
        main_container = tk.Frame(self.root, bg=ColorScheme.BG_DARK)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Two-column layout
        content_frame = tk.Frame(main_container, bg=ColorScheme.BG_DARK)
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Left panel - Configuration
        left_panel = tk.Frame(content_frame, bg=ColorScheme.BG_DARK)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.create_control_section(left_panel)
        self.create_config_section(left_panel)
        
        # Right panel - Logs
        right_panel = tk.Frame(content_frame, bg=ColorScheme.BG_DARK, width=500)
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.pack_propagate(False)
        
        self.create_log_section(right_panel)
    
    def create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=ColorScheme.BG_DARK)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title with ASCII art
        title_text = """
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃   ◈ Re-Mass DM Control Panel ◈          ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
      [ Re-DM Users from Bot DM History ]
        """
        
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=("Courier New", 10),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_DARK,
            justify="center"
        )
        title_label.pack()
    
    def create_control_section(self, parent):
        """Create the control buttons section."""
        control_frame = tk.LabelFrame(
            parent,
            text=" [ OPERATION CONTROL ] ",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM,
            relief="solid",
            borderwidth=1
        )
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Status indicator
        status_frame = tk.Frame(control_frame, bg=ColorScheme.BG_MEDIUM)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            status_frame,
            text=">> Status:",
            font=("Courier New", 10),
            fg=ColorScheme.TEXT_SECONDARY,
            bg=ColorScheme.BG_MEDIUM
        ).pack(side="left")
        
        self.status_label = tk.Label(
            status_frame,
            text="◆ IDLE",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM
        )
        self.status_label.pack(side="left", padx=10)
        
        # Control buttons
        btn_frame = tk.Frame(control_frame, bg=ColorScheme.BG_MEDIUM)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ START RE-MASS DM",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.BG_DARK,
            bg=ColorScheme.BTN_PRIMARY,
            activeforeground=ColorScheme.BG_DARK,
            activebackground=ColorScheme.HOVER_LIGHT,
            command=self.start_operation,
            cursor="hand2",
            relief="raised",
            borderwidth=2
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="■ STOP",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.BG_DARK,
            bg=ColorScheme.ACCENT_SECONDARY,
            activeforeground=ColorScheme.BG_DARK,
            activebackground=ColorScheme.HOVER_LIGHT,
            command=self.stop_operation,
            cursor="hand2",
            relief="raised",
            borderwidth=2,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
    
    def create_config_section(self, parent):
        """Create the configuration section."""
        config_frame = tk.LabelFrame(
            parent,
            text=" [ CONFIGURATION ] ",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM,
            relief="solid",
            borderwidth=1
        )
        config_frame.pack(fill="both", expand=True)
        
        # Scrollable frame for config fields
        canvas = tk.Canvas(config_frame, bg=ColorScheme.BG_MEDIUM, highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ColorScheme.BG_MEDIUM)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bot Tokens Section
        self.create_tokens_section(scrollable_frame)
        
        # Message Section
        self.create_message_section(scrollable_frame)
        
        # Delay Configuration
        self.create_delay_section(scrollable_frame)
    
    def create_tokens_section(self, parent):
        """Create bot tokens configuration section."""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_MEDIUM)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        tk.Label(
            section_frame,
            text=">> Bot Tokens",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM
        ).pack(anchor="w", pady=(0, 5))
        
        # Instructions
        tk.Label(
            section_frame,
            text="Add bot tokens (one per line). First token = controller, rest = senders.",
            font=("Courier New", 8),
            fg=ColorScheme.TEXT_MUTED,
            bg=ColorScheme.BG_MEDIUM,
            wraplength=450,
            justify="left"
        ).pack(anchor="w", pady=(0, 5))
        
        # Token text area
        self.tokens_text = scrolledtext.ScrolledText(
            section_frame,
            height=8,
            font=("Courier New", 9),
            bg=ColorScheme.BG_LIGHT,
            fg=ColorScheme.TEXT_PRIMARY,
            insertbackground=ColorScheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1
        )
        self.tokens_text.pack(fill="x", pady=5)
    
    def create_message_section(self, parent):
        """Create message configuration section."""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_MEDIUM)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        tk.Label(
            section_frame,
            text=">> Message to Send",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM
        ).pack(anchor="w", pady=(0, 5))
        
        # Instructions
        tk.Label(
            section_frame,
            text="Enter the message to re-send to users (note: embed content is hardcoded).",
            font=("Courier New", 8),
            fg=ColorScheme.TEXT_MUTED,
            bg=ColorScheme.BG_MEDIUM,
            wraplength=450,
            justify="left"
        ).pack(anchor="w", pady=(0, 5))
        
        # Message text area
        self.message_text_widget = scrolledtext.ScrolledText(
            section_frame,
            height=4,
            font=("Courier New", 9),
            bg=ColorScheme.BG_LIGHT,
            fg=ColorScheme.TEXT_PRIMARY,
            insertbackground=ColorScheme.TEXT_PRIMARY,
            relief="solid",
            borderwidth=1
        )
        self.message_text_widget.pack(fill="x", pady=5)
        self.message_text_widget.insert("1.0", "Check out this new update!")
    
    def create_delay_section(self, parent):
        """Create delay configuration section."""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_MEDIUM)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Section title
        tk.Label(
            section_frame,
            text=">> Timing Configuration",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM
        ).pack(anchor="w", pady=(0, 5))
        
        # DM Delay
        delay_frame = tk.Frame(section_frame, bg=ColorScheme.BG_MEDIUM)
        delay_frame.pack(fill="x", pady=5)
        
        tk.Label(
            delay_frame,
            text="DM Delay (seconds):",
            font=("Courier New", 9),
            fg=ColorScheme.TEXT_SECONDARY,
            bg=ColorScheme.BG_MEDIUM
        ).pack(side="left")
        
        self.dm_delay_var = tk.StringVar(value="0.10")
        delay_entry = tk.Entry(
            delay_frame,
            textvariable=self.dm_delay_var,
            font=("Courier New", 9),
            bg=ColorScheme.BG_LIGHT,
            fg=ColorScheme.TEXT_PRIMARY,
            insertbackground=ColorScheme.TEXT_PRIMARY,
            width=10,
            relief="solid",
            borderwidth=1
        )
        delay_entry.pack(side="left", padx=10)
    
    def create_log_section(self, parent):
        """Create the live logs section."""
        log_frame = tk.LabelFrame(
            parent,
            text=" [ LIVE LOGS ] ",
            font=("Courier New", 10, "bold"),
            fg=ColorScheme.TEXT_PRIMARY,
            bg=ColorScheme.BG_MEDIUM,
            relief="solid",
            borderwidth=1
        )
        log_frame.pack(fill="both", expand=True)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier New", 8),
            bg=ColorScheme.BG_LIGHT,
            fg=ColorScheme.TEXT_PRIMARY,
            state="disabled",
            wrap="word",
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure tags for colored logs
        self.log_text.tag_config("INFO", foreground=ColorScheme.TEXT_PRIMARY)
        self.log_text.tag_config("SUCCESS", foreground=ColorScheme.ACCENT_PRIMARY)
        self.log_text.tag_config("WARNING", foreground=ColorScheme.ACCENT_SECONDARY)
        self.log_text.tag_config("ERROR", foreground=ColorScheme.TEXT_SECONDARY)
        
        # Clear button
        clear_btn = tk.Button(
            log_frame,
            text="🗑 CLEAR LOGS",
            font=("Courier New", 9),
            fg=ColorScheme.BG_DARK,
            bg=ColorScheme.ACCENT_SECONDARY,
            command=self.clear_logs,
            cursor="hand2",
            relief="raised",
            borderwidth=1
        )
        clear_btn.pack(pady=(0, 10))
    
    def start_operation(self):
        """Start the re-mass DM operation."""
        if self.operation_running:
            messagebox.showwarning("Already Running", "Operation is already in progress!")
            return
        
        # Get tokens
        tokens_text = self.tokens_text.get("1.0", "end-1c").strip()
        if not tokens_text:
            messagebox.showerror("Error", "Please add at least 2 bot tokens!")
            return
        
        self.tokens = [t.strip() for t in tokens_text.split('\n') if t.strip()]
        
        if len(self.tokens) < 2:
            messagebox.showerror("Error", "Need at least 2 tokens (1 controller + 1 sender)!")
            return
        
        # Get message
        self.message_text = self.message_text_widget.get("1.0", "end-1c").strip()
        if not self.message_text:
            messagebox.showerror("Error", "Please enter a message to send!")
            return
        
        # Get delay
        try:
            self.dm_delay = float(self.dm_delay_var.get())
            if self.dm_delay < 0:
                raise ValueError("Delay must be non-negative")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid DM delay value: {e}")
            return
        
        # Update UI
        self.operation_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.update_status("◆ RUNNING", ColorScheme.ACCENT_PRIMARY)
        
        # Start operation in background thread
        self.operation_thread = threading.Thread(target=self.run_remassdm_operation, daemon=True)
        self.operation_thread.start()
        
        self.add_log("Re-Mass DM operation started!", "SUCCESS")
    
    def stop_operation(self):
        """Stop the re-mass DM operation."""
        if not self.operation_running:
            return
        
        self.operation_running = False
        self.update_status("◆ STOPPING...", ColorScheme.ACCENT_SECONDARY)
        self.add_log("Stopping operation...", "WARNING")
        
        # Update UI
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def run_remassdm_operation(self):
        """Run the re-mass DM operation in a background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async operation
            loop.run_until_complete(self.async_remassdm_operation())
            
        except Exception as e:
            self.logger.error(f"Operation error: {e}")
            self.add_log(f"ERROR: {e}", "ERROR")
        finally:
            self.operation_running = False
            self.root.after(0, lambda: self.update_status("◆ IDLE", ColorScheme.TEXT_SECONDARY))
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
    
    async def async_remassdm_operation(self):
        """Async function to perform re-mass DM operation."""
        # Setup Discord clients
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        self.sender_clients = []
        self.sender_meta = {}
        
        sender_tokens = self.tokens[1:]  # Skip controller token for now
        self.logger.info(f"Starting Re-Mass DM operation...")
        self.logger.info(f"Logging in {len(sender_tokens)} sender clients...")
        
        # Login sender clients
        login_tasks = []
        for idx, token in enumerate(sender_tokens):
            if not token or token.strip() == "":
                self.logger.warning(f"Skipping empty token at position {idx+1}")
                continue
            
            try:
                client = discord.Client(intents=intents)
                self.sender_clients.append(client)
                self.sender_meta[client] = {
                    "index": idx,
                    "token": token,
                    "dead": False
                }
                
                self.logger.info(f"Initiating login for Sender_{idx}...")
                
                async def login_sender(c, t, i):
                    try:
                        await c.login(t)
                        await c.connect(reconnect=False)
                    except Exception as e:
                        self.logger.error(f"Sender_{i} login failed: {e}")
                        self.sender_meta[c]["dead"] = True
                
                task = asyncio.create_task(login_sender(client, token, idx))
                login_tasks.append(task)
                
            except Exception as e:
                self.logger.error(f"Failed to create Sender_{idx}: {e}")
        
        # Let logins happen in background, give them time to connect
        self.logger.info("Waiting for clients to connect...")
        await asyncio.sleep(3)
        self.logger.info("Connection phase complete, checking status...")
        
        alive_count = sum(1 for c in self.sender_clients if not self.sender_meta.get(c, {}).get("dead", False))
        self.logger.info(f"✓ Sender clients ready: {alive_count}/{len(self.sender_clients)} alive")
        
        if alive_count == 0:
            self.logger.error("No available sender bots!")
            return
        
        # Phase 1: Scan DM channels
        self.logger.info("=== SCANNING PHASE ===")
        scanned_users = set()
        
        available_senders = [c for c in self.sender_clients if not self.sender_meta.get(c, {}).get("dead", False)]
        
        for sender in available_senders:
            if not self.operation_running:
                break
            
            sender_idx = self.sender_meta[sender]["index"]
            sender_label = f"Sender_{sender_idx}"
            
            user_ids = await self.scan_bot_dm_channels(sender, sender_label)
            for user_id in user_ids:
                scanned_users.add(user_id)
        
        total_users = len(scanned_users)
        self.logger.info(f"Total unique users found: {total_users}")
        
        if total_users == 0:
            self.logger.warning("No existing DM channels found!")
            return
        
        # Phase 2: Re-DM users
        self.logger.info("=== RE-DM PHASE ===")
        users_to_dm = list(scanned_users)
        
        # Shared counters for tracking progress (with lock for thread safety)
        self.dm_stats = {
            "sent": 0,
            "failed": 0,
            "total": total_users
        }
        self.dm_stats_lock = asyncio.Lock()  # Protect counter updates
        
        # Distribute users across bots
        users_per_bot = len(users_to_dm) // len(available_senders)
        if users_per_bot == 0:
            users_per_bot = 1
        
        self.logger.info(f"Distributing {total_users} users across {len(available_senders)} bots (~{users_per_bot} users per bot)")
        
        # Create worker tasks
        worker_tasks = []
        for idx, sender in enumerate(available_senders):
            start_idx = idx * users_per_bot
            end_idx = start_idx + users_per_bot if idx < len(available_senders) - 1 else len(users_to_dm)
            assigned_users = users_to_dm[start_idx:end_idx]
            
            sender_idx = self.sender_meta[sender]["index"]
            self.logger.info(f"Starting worker for Sender_{sender_idx} with {len(assigned_users)} users")
            task = asyncio.create_task(
                self.bot_worker(sender, sender_idx, assigned_users)
            )
            worker_tasks.append(task)
        
        # Wait for all workers
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        
        self.logger.info("=== RE-MASS DM COMPLETE ===")
        self.logger.info(f"Total: {total_users} | Sent: {self.dm_stats['sent']} | Failed: {self.dm_stats['failed']}")
        self.logger.info(f"Operation finished!")
        
        # Cleanup
        for client in self.sender_clients:
            try:
                await client.close()
            except:
                pass
    
    async def scan_bot_dm_channels(self, sender, sender_label):
        """Scan a bot's existing DM channels and return list of user IDs."""
        user_ids = []
        
        try:
            await sender.wait_until_ready()
            
            for channel in sender.private_channels:
                if isinstance(channel, discord.DMChannel) and channel.recipient:
                    user_ids.append(channel.recipient.id)
            
            self.logger.info(f"[{sender_label}] Found {len(user_ids)} existing DM channels")
            
        except Exception as e:
            self.logger.error(f"[{sender_label}] Error scanning DM channels: {e}")
        
        return user_ids
    
    async def bot_worker(self, sender, sender_index, user_ids_subset):
        """Worker function for each bot."""
        sender_label = f"Sender_{sender_index}"
        self.logger.info(f"[Bot worker {sender_index}] Starting with {len(user_ids_subset)} users")
        
        for user_id in user_ids_subset:
            if not self.operation_running:
                break
            
            if self.sender_meta.get(sender, {}).get("dead", False):
                self.logger.warning(f"[Bot worker {sender_index}] Stopped - bot is dead")
                break
            
            await self.send_dm_to_user(sender, sender_label, user_id)
        
        self.logger.info(f"[Bot worker {sender_index}] Completed")
    
    async def send_dm_to_user(self, sender, sender_label, user_id):
        """Send DM to a user."""
        try:
            # Check if sender is still valid
            if self.sender_meta.get(sender, {}).get("dead", False):
                return False
            
            self.logger.info(f"[{sender_label}] Re-DMing user {user_id}...")
            
            # Create embed
            embed = discord.Embed(
                title="THEY HAVING LESBIAN ESEX ON CAM",
                description="verify below to never miss a stage from gio and 24/7 camgirls.\n if u dont verify u might never see a stage again 👀.",
                color=0
            )
            
            embed.set_image(url="https://media.discordapp.net/attachments/1469864352197771382/1472489934509310097/image.png?ex=6992c29d&is=6991711d&hm=17597fe1dbca4ae34347d842d6390a377fa310f4fe27812b890abf25ce950912&=&format=webp&quality=lossless")
            
            # Create button
            from discord.ui import Button, View
            class VerifyButton(View):
                def __init__(self):
                    super().__init__(timeout=None)
                    self.add_item(Button(
                        label="Join camshow server",
                        style=discord.ButtonStyle.link,
                        url="https://discord.com/oauth2/authorize?client_id=1467682706430234706&redirect_uri=https%3A%2F%2Frestorecord.com%2Fapi%2Fcallback&response_type=code&scope=identify+guilds.join&state=1469518705712038105&prompt=none"
                    ))
            
            view = VerifyButton()
            
            # Send DM
            user = discord.Object(id=user_id)
            channel = await sender.create_dm(user)
            await channel.send(content=None, embed=embed, view=view)
            
            # Update stats (thread-safe)
            async with self.dm_stats_lock:
                self.dm_stats['sent'] += 1
            
            self.logger.info(f"[{sender_label}] ✓ Success for user {user_id}!")
            
            await asyncio.sleep(self.dm_delay)
            return True
            
        except Exception as e:
            # Update stats (thread-safe)
            async with self.dm_stats_lock:
                self.dm_stats['failed'] += 1
            
            self.logger.error(f"[{sender_label}] ✗ Failed for user {user_id}: {e}")
            
            msg = str(e).lower()
            if "401" in msg or "unauthorized" in msg or "spam" in msg or "captcha" in msg:
                self.logger.warning(f"[{sender_label}] ⚠ Bot has been flagged/disabled")
                self.sender_meta[sender]["dead"] = True
                return False
            
            return False
    
    def update_status(self, status_text, color):
        """Update the status label."""
        self.status_label.config(text=status_text, fg=color)
    
    def add_log(self, message, tag="INFO"):
        """Add a log message to the log viewer."""
        self.log_queue.put((message, tag))
    
    def update_logs(self):
        """Update logs from the queue."""
        try:
            while not self.log_queue.empty():
                item = self.log_queue.get_nowait()
                
                if isinstance(item, tuple):
                    message, tag = item
                else:
                    message = item
                    tag = "INFO"
                
                self.log_text.config(state="normal")
                self.log_text.insert("end", f"{message}\n", tag)
                self.log_text.see("end")
                self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_logs)
    
    def clear_logs(self):
        """Clear the log viewer."""
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.logger.info("Logs cleared")
    
    def on_closing(self):
        """Handle window close event."""
        if self.operation_running:
            if messagebox.askokcancel("Quit", "Operation is running. Stop and quit?"):
                self.operation_running = False
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = RemassDMPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
