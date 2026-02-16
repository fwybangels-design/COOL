# mass_dm_bot_verify_button.py
# WARNING: Replace placeholder tokens with your real tokens locally.
# Mass-DMing large numbers of users may violate Discord TOS. Use responsibly.

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

    sent_count = 0
    failed_count = 0
    start_time = time.time()
    controller_label = user_label_from_user_obj(getattr(bot, "user", None))

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

    if sender_clients:
        for _ in range(20):
            if all(getattr(c, "is_ready", lambda: False)() or sender_meta.get(c, {}).get("dead", False) for c in sender_clients):
                break
            await asyncio.sleep(1)

    with open("massdm.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nMass DM started by {ctx.author} in {ctx.guild.name} ({ctx.guild.id})\n")
        log_file.write(f"Message: {message}\n\n")

        available_senders = [
            s for s in sender_clients
            if getattr(s, "is_ready", lambda: False)() and s.get_guild(ctx.guild.id) is not None and not sender_meta.get(s, {}).get("dead", False)
        ]
        client_index = 0
        total_senders = len(available_senders)

        for member in ctx.guild.members:
            if not dm_active:
                break
            if member.bot or member == bot.user:
                continue

            used_sender = None
            used_label = controller_label

            if total_senders > 0 and available_senders:
                attempts = 0
                while attempts < total_senders:
                    candidate = available_senders[client_index % total_senders]
                    client_index += 1
                    attempts += 1

                    if sender_meta.get(candidate, {}).get("dead", False):
                        available_senders.remove(candidate)
                        total_senders = len(available_senders)
                        continue
                    if not getattr(candidate, "is_ready", lambda: False)():
                        available_senders.remove(candidate)
                        total_senders = len(available_senders)
                        continue
                    if candidate.get_guild(ctx.guild.id) is None:
                        available_senders.remove(candidate)
                        total_senders = len(available_senders)
                        continue

                    used_sender = candidate
                    used_label = user_label_from_user_obj(getattr(used_sender, "user", None))
                    break

            log_message = f"{used_label}  Attempting to DM {member} ({member.id})... "
            print(log_message, end="")
            log_file.write(log_message)

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
                    user = await used_sender.fetch_user(member.id)
                    await user.send(content=None, embed=embed, view=view)
                else:
                    await member.send(content=None, embed=embed, view=view)

                sent_count += 1
                print("Success!")
                log_file.write("Success!\n")

            except Exception as e:
                failed_count += 1
                error_message = f"Failed: {e}"
                print(error_message)
                log_file.write(error_message + "\n")

                try:
                    msg = str(e).lower()
                    if used_sender is not None and ("401" in msg or "unauthorized" in msg or isinstance(e, discord.LoginFailure)):
                        sender_meta[used_sender]["dead"] = True
                        try:
                            available_senders.remove(used_sender)
                        except Exception:
                            pass
                        total_senders = len(available_senders)
                except Exception:
                    pass

            elapsed_time = int(time.time() - start_time)
            try:
                await status_message.edit(content=(
                    f"**Mass DM Operation In Progress**\n"
                    f"Message: {message}\n"
                    f"Total Members: {len(ctx.guild.members)}\n"
                    f"Time Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n"
                    f"----------------------------------------\n"
                    f"DMing: {member} ({member.id})\n"
                    f"Status: {'Success' if member.dm_channel else 'Failed'}\n"
                    f"People DMed: {sent_count}\n"
                    f"People Failed to DM: {failed_count}\n"
                    f"Time Elapsed: {elapsed_time} seconds"
                ))
            except Exception:
                pass

            await asyncio.sleep(0.2)

    try:
        await ctx.author.send(f'Message sent to {sent_count} members. Failed to send to {failed_count} members.')
    except Exception:
        pass

    dm_active = False

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
