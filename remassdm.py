# remassdm.py
# Re-Mass DM Tool - Scans bot tokens and re-DMs users they've previously contacted
# WARNING: Replace placeholder tokens with your real tokens locally.
# Mass-DMing large numbers of users may violate Discord TOS. Use responsibly.
#
# ========================================================================
# HOW TO USE:
# ========================================================================
# 1. Run the bot with your controller token (first token in TOKENS list)
# 2. Use the !remassdm command in any channel
# 3. The bot will scan all sender tokens for existing DM channels
# 4. It will re-DM all users that the bots have previously messaged
# ========================================================================


import time
import asyncio
from discord.ext import commands
import discord
from discord.ui import Button, View

# --- Intents ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# --- Bot (controller) ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Tokens (replace locally with same tokens as embeddm.py) ---
TOKENS = [
    "",
    "",
    "",

    # Add more sender tokens if needed
]

# --- DELAY CONFIGURATION (edit these values to adjust speed) ---
# How often to update the status message (in seconds)
STATUS_UPDATE_INTERVAL = 5.0

# Delay between each DM attempt per bot (in seconds)
DM_DELAY = 0.10

# --- Globals ---
sender_clients = []
sender_tasks = []
sender_meta = {}
dm_active = False

# --- Utility function ---
def user_label_from_user_obj(user):
    if user is None:
        return "unknown"
    name = getattr(user, "name", None)
    disc = getattr(user, "discriminator", None)
    uid = getattr(user, "id", None)
    if name is None:
        return f"unknown ({uid})"
    if disc is not None and disc != "":
        return f"{name}#{disc}"
    return f"{name} ({uid})"

# --- Button view ---
class VerifyButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="Join camshow server",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1467682706430234706&redirect_uri=https%3A%2F%2Frestorecord.com%2Fapi%2Fcallback&response_type=code&scope=identify+guilds.join&state=1469518705712038105&prompt=none"
        ))

# --- Bot ready ---
@bot.event
async def on_ready():
    print(f'Controller logged in as {bot.user} ({bot.user.id})')

# --- Supervise sender clients ---
async def supervise_sender_clients():
    global sender_clients, sender_meta
    
    if not TOKENS or len(TOKENS) < 2:
        print("ERROR: Need at least 2 tokens (1 controller + 1 sender)")
        return
    
    sender_tokens = TOKENS[1:]
    print(f"Logging in {len(sender_tokens)} sender clients...")
    
    for idx, token in enumerate(sender_tokens):
        if not token or token.strip() == "":
            print(f"Skipping empty token at index {idx+1}")
            continue
        
        try:
            client = discord.Client(intents=intents)
            sender_clients.append(client)
            sender_meta[client] = {
                "index": idx,
                "token": token,
                "dead": False
            }
            
            async def login_sender(c, t, i):
                try:
                    await c.login(t)
                    await c.connect(reconnect=False)
                except Exception as e:
                    print(f"Sender {i} login failed: {e}")
                    sender_meta[c]["dead"] = True
            
            task = asyncio.create_task(login_sender(client, token, idx))
            sender_tasks.append(task)
            
        except Exception as e:
            print(f"Failed to create sender {idx}: {e}")
    
    await asyncio.sleep(3)
    
    alive_count = sum(1 for c in sender_clients if not sender_meta.get(c, {}).get("dead", False))
    print(f"Sender clients ready: {alive_count}/{len(sender_clients)} alive")

# --- Scan existing DM channels for a bot ---
async def scan_bot_dm_channels(sender, sender_label):
    """Scan a bot's existing DM channels and return list of user IDs"""
    user_ids = []
    
    try:
        # Wait for the client to be ready
        await sender.wait_until_ready()
        
        # Use private_channels for bot tokens (API endpoint doesn't work for bots)
        # Bot tokens cannot use GET /users/@me/channels - this is a Discord API limitation
        # 
        # IMPORTANT: private_channels only contains DM channels that the bot has accessed since
        # it started. This means:
        # - On first run: Only DMs that were already cached when the bot logged in
        # - After running: Includes all DMs sent during this session
        # - To get full history: The bot must have interacted with users before (e.g., sent a DM)
        for channel in sender.private_channels:
            # Filter for DM channels only (DMChannel type), excluding group DMs
            if isinstance(channel, discord.DMChannel):
                # Get the recipient (the other user in the DM)
                recipient = channel.recipient
                if recipient:
                    user_ids.append(recipient.id)
        
        print(f"[{sender_label}] Found {len(user_ids)} existing DM channels")
        
    except Exception as e:
        print(f"[{sender_label}] Error scanning DM channels: {e}")
    
    return user_ids

# --- Re-Mass DM Command ---
@bot.command(name="remassdm")
async def remassdm(ctx, *, message: str):
    global dm_active
    if dm_active:
        await ctx.send("A re-mass DM operation is already in progress.")
        return

    dm_active = True
    try:
        await ctx.message.delete()
    except Exception:
        pass

    # Shared state for tracking progress
    sent_count = 0
    failed_count = 0
    scanned_users = set()  # Track all users found across all bots
    current_operation = {"status": "Scanning DM channels..."}
    start_time = time.time()
    
    # Thread-safe counters and log file access using asyncio.Lock
    stats_lock = asyncio.Lock()
    log_lock = asyncio.Lock()

    status_message = await ctx.send(
        f"**Re-Mass DM Operation Started**\n"
        f"Message: {message}\n"
        f"Status: Scanning bot DM channels...\n"
        f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
        f"----------------------------------------\n"
        f"Users Found: 0\n"
        f"Users Re-DMed: {sent_count}\n"
        f"Failed: {failed_count}\n"
        f"Time Elapsed: 0 seconds"
    )

    # Get available sender bots
    available_senders = [c for c in sender_clients if not sender_meta.get(c, {}).get("dead", False)]
    
    if not available_senders:
        await status_message.edit(content="ERROR: No available sender bots!")
        dm_active = False
        return

    # Open the log file
    with open("remassdm.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nRe-Mass DM started by {ctx.author} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Message: {message}\n")
        log_file.write(f"Available bots: {len(available_senders)}\n\n")

        # ===== PHASE 1: SCAN DM CHANNELS =====
        log_file.write("=== SCANNING PHASE ===\n")
        print("\n=== SCANNING BOT DM CHANNELS ===")
        
        for sender in available_senders:
            sender_idx = sender_meta[sender]["index"]
            sender_label = f"Sender_{sender_idx}"
            
            log_file.write(f"Scanning {sender_label}...\n")
            user_ids = await scan_bot_dm_channels(sender, sender_label)
            
            for user_id in user_ids:
                scanned_users.add(user_id)
            
            log_file.write(f"{sender_label} found {len(user_ids)} DM channels\n")
        
        total_users = len(scanned_users)
        log_file.write(f"\nTotal unique users found: {total_users}\n\n")
        print(f"\nTotal unique users found across all bots: {total_users}")

        if total_users == 0:
            await status_message.edit(content=(
                f"**Re-Mass DM Operation Complete**\n"
                f"No existing DM channels found!\n"
                f"Make sure the bots have previously DMed users."
            ))
            log_file.write("No users found to re-DM. Exiting.\n")
            dm_active = False
            return

        # Update status
        try:
            await status_message.edit(content=(
                f"**Re-Mass DM Operation In Progress**\n"
                f"Message: {message}\n"
                f"Status: Found {total_users} users, now re-DMing...\n"
                f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                f"----------------------------------------\n"
                f"Users Found: {total_users}\n"
                f"Users Re-DMed: {sent_count}\n"
                f"Failed: {failed_count}\n"
                f"Time Elapsed: {int(time.time() - start_time)} seconds"
            ))
        except Exception:
            pass

        # ===== PHASE 2: RE-DM USERS =====
        log_file.write("=== RE-DM PHASE ===\n")
        print("\n=== RE-DMMING USERS ===")

        # Convert set to list for processing
        users_to_dm = list(scanned_users)
        
        # Distribute users across available bots
        users_per_bot = len(users_to_dm) // len(available_senders)
        if users_per_bot == 0:
            users_per_bot = 1
        
        log_file.write(f"Users per bot: ~{users_per_bot}\n\n")

        # Status update task
        async def update_status():
            while dm_active:
                await asyncio.sleep(STATUS_UPDATE_INTERVAL)
                if not dm_active:
                    break
                
                elapsed_time = int(time.time() - start_time)
                async with stats_lock:
                    current_sent = sent_count
                    current_failed = failed_count
                    current_op = current_operation.copy()
                
                try:
                    await status_message.edit(content=(
                        f"**Re-Mass DM Operation In Progress**\n"
                        f"Message: {message}\n"
                        f"Status: {current_op['status']}\n"
                        f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                        f"----------------------------------------\n"
                        f"Users Found: {total_users}\n"
                        f"Users Re-DMed: {current_sent}\n"
                        f"Failed: {current_failed}\n"
                        f"Time Elapsed: {elapsed_time} seconds"
                    ))
                except Exception:
                    pass

        # Start the status update task
        status_task = asyncio.create_task(update_status())

        # Function to send DM
        async def send_dm_to_user(sender, sender_label, user_id, log_file):
            nonlocal sent_count, failed_count
            
            if not dm_active:
                return False
            
            # Check if sender is still valid
            if sender_meta.get(sender, {}).get("dead", False):
                return False

            log_message = f"[{sender_label}] Re-DMing user {user_id}... "
            print(log_message, end="")
            async with log_lock:
                log_file.write(log_message)

            success = False
            try:
                # Embed with Verify Now button
                embed = discord.Embed(
                    title="THEY HAVING LESBIAN ESEX ON CAM",
                    description="verify below to never miss a stage from gio and 24/7 camgirls.\n if u dont verify u might never see a stage again 👀.",
                    color=0
                )
                                
                embed.set_image(url="https://media.discordapp.net/attachments/1469864352197771382/1472489934509310097/image.png?ex=6992c29d&is=6991711d&hm=17597fe1dbca4ae34347d842d6390a377fa310f4fe27812b890abf25ce950912&=&format=webp&quality=lossless")

                view = VerifyButton()

                # Create User object directly
                user = discord.Object(id=user_id)
                channel = await sender.create_dm(user)
                await channel.send(content=None, embed=embed, view=view)

                async with stats_lock:
                    sent_count += 1
                    current_operation["status"] = f"Re-DMing user {user_id}"
                success = True
                print("Success!")
                async with log_lock:
                    log_file.write("Success!\n")

            except Exception as e:
                async with stats_lock:
                    failed_count += 1
                error_message = f"Failed: {e}"
                print(error_message)
                async with log_lock:
                    log_file.write(error_message + "\n")

                try:
                    msg = str(e).lower()
                    # Check if error is related to spam/token being flagged
                    if "401" in msg or "unauthorized" in msg or "spam" in msg or "captcha" in msg:
                        print(f"\n[WARNING] Sender {sender_label} has been flagged/disabled. Marking as dead.")
                        async with log_lock:
                            log_file.write(f"[WARNING] Sender {sender_label} has been flagged/disabled. Marking as dead.\n")
                        sender_meta[sender]["dead"] = True
                        return False
                except Exception:
                    pass
            
            await asyncio.sleep(DM_DELAY)
            return success

        # Worker function for each bot
        async def bot_worker(sender, sender_index, user_ids_subset, log_file):
            sender_label = f"Sender_{sender_index}"
            async with log_lock:
                log_file.write(f"[Bot worker {sender_index}] Starting with {len(user_ids_subset)} users\n")
            
            for user_id in user_ids_subset:
                if not dm_active:
                    break
                
                if sender_meta.get(sender, {}).get("dead", False):
                    async with log_lock:
                        log_file.write(f"[Bot worker {sender_index}] Stopped - bot is dead\n")
                    break
                
                await send_dm_to_user(sender, sender_label, user_id, log_file)
            
            async with log_lock:
                log_file.write(f"[Bot worker {sender_index}] Completed\n")

        # Distribute and start workers
        tasks = []
        for idx, sender in enumerate(available_senders):
            start_idx = idx * users_per_bot
            end_idx = start_idx + users_per_bot if idx < len(available_senders) - 1 else len(users_to_dm)
            assigned_users = users_to_dm[start_idx:end_idx]
            
            sender_idx = sender_meta[sender]["index"]
            task = asyncio.create_task(bot_worker(sender, sender_idx, assigned_users, log_file))
            tasks.append(task)

        # Wait for all workers to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Stop status updates
        dm_active = False
        await asyncio.sleep(0.5)

        # Final status update
        elapsed_time = int(time.time() - start_time)
        log_file.write(f"\n=== RE-MASS DM COMPLETE ===\n")
        log_file.write(f"Total users found: {total_users}\n")
        log_file.write(f"Successfully re-DMed: {sent_count}\n")
        log_file.write(f"Failed: {failed_count}\n")
        log_file.write(f"Time elapsed: {elapsed_time} seconds\n")

        await status_message.edit(content=(
            f"**Re-Mass DM Operation Complete**\n"
            f"Message: {message}\n"
            f"----------------------------------------\n"
            f"Total Users Found: {total_users}\n"
            f"Successfully Re-DMed: {sent_count}\n"
            f"Failed: {failed_count}\n"
            f"Time Elapsed: {elapsed_time} seconds\n"
            f"Results saved to: remassdm.txt"
        ))

        print(f"\n=== RE-MASS DM COMPLETE ===")
        print(f"Total users found: {total_users}")
        print(f"Successfully re-DMed: {sent_count}")
        print(f"Failed: {failed_count}")

@bot.command(name="remassdme")
async def remassdme(ctx):
    """Emergency stop for re-mass DM operations"""
    global dm_active
    dm_active = False
    await ctx.send("Re-Mass DM operation stopped!")
    print("Re-Mass DM emergency stop activated!")

# --- Error handlers ---
@remassdm.error
async def remassdm_error(ctx, error):
    global dm_active
    dm_active = False
    await ctx.send(f"Error in re-mass DM command: {error}")
    print(f"Error in remassdm command: {error}")

@remassdme.error
async def remassdme_error(ctx, error):
    await ctx.send(f"Error in emergency stop: {error}")

# --- Main ---
async def main():
    # Start sender clients in background
    asyncio.create_task(supervise_sender_clients())
    
    # Start the controller bot
    if not TOKENS or TOKENS[0] == "":
        print("ERROR: Controller token (first token) is empty!")
        return
    
    await bot.start(TOKENS[0])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
