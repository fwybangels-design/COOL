#!/usr/bin/env python3
"""
open_pending_apps.py
Opens every pending membership application in the server one by one,
sends a message inside each interview channel, then moves on.

Usage:
    python open_pending_apps.py               # uses message from config
    python open_pending_apps.py "custom msg"  # custom one-off message

Delay between applications can be tuned with DELAY_BETWEEN_APPS below.
"""

import os
import sys
import time
import json
import random
import logging
import requests

# ---------------------------------------------------------------------------
# Configuration — edit these values directly
# ---------------------------------------------------------------------------

# Your Discord user token
TOKEN = os.environ.get("DISCORD_TOKEN", "").strip()
if TOKEN.startswith("Bot "):
    TOKEN = TOKEN[4:].strip()

# The Discord server/guild ID to process applications for
GUILD_ID = "1464067001256509452"

# Message sent inside each interview channel when an application is opened
AUTH_REQUEST_MESSAGE = (
    "🔐 **Discord Bot Authorization Required**\n\n"
    "To join this server, you need to authorize our Discord bot.\n\n"
    "**How it works:**\n"
    "1. Click the authorization link below\n"
    "2. Review and accept the bot permissions\n"
    "3. Once authorized, you'll be **automatically accepted within 2-3 seconds!** ⚡"
)

# How long (seconds) to wait for Discord to create the interview channel
CHANNEL_CREATION_WAIT = 2

# Default retry delay (seconds) when rate-limited
RETRY_AFTER_DEFAULT = 2

# Extra cookies for API requests (leave empty unless needed)
COOKIES = {}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tune this value to change the pace (seconds between each application)
# 2-3 seconds is "not too fast but not too slow"
# ---------------------------------------------------------------------------
DELAY_BETWEEN_APPS = 2.5


def get_headers():
    """Return Discord API headers using the configured user token."""
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": TOKEN,
        "origin": "https://discord.com",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
    }


def get_pending_applications():
    """
    Fetch all pending join-request applications from Discord.
    Returns a list of dicts with at least 'id' (request_id) and
    'user' -> 'id' (user_id).
    Handles pagination automatically.
    """
    all_requests = []
    base_url = f"https://discord.com/api/v9/guilds/{GUILD_ID}/requests"
    headers = get_headers()
    params = {"status": "SUBMITTED", "limit": 100}

    while True:
        try:
            resp = requests.get(base_url, headers=headers, cookies=COOKIES,
                                params=params, timeout=10)
            if resp.status_code == 429:
                retry_after = resp.json().get("retry_after", RETRY_AFTER_DEFAULT)
                logger.warning(f"Rate limited — waiting {retry_after}s")
                time.sleep(retry_after)
                continue
            if resp.status_code != 200:
                logger.error(
                    f"Failed to fetch applications. "
                    f"Status: {resp.status_code} — {resp.text}"
                )
                break

            data = resp.json()
            # Discord returns either a list directly or {"guild_join_requests": [...]}
            if isinstance(data, list):
                batch = data
            else:
                batch = data.get("guild_join_requests", [])

            all_requests.extend(batch)

            # If fewer results than the limit were returned, we've reached the end
            if len(batch) < 100:
                break

            # Use the last request's ID as the cursor for the next page
            params = {"status": "SUBMITTED", "limit": 100, "after": batch[-1]["id"]}
        except Exception as e:
            logger.error(f"Exception fetching applications: {e}")
            break

    return all_requests


def open_interview(request_id):
    """Open the interview channel for a join-request."""
    url = f"https://discord.com/api/v9/join-requests/{request_id}/interview"
    headers = get_headers()
    headers["referer"] = f"https://discord.com/channels/{GUILD_ID}/member-safety"
    headers["content-type"] = "application/json"
    try:
        resp = requests.post(url, headers=headers, cookies=COOKIES, timeout=10)
        if resp.status_code == 429:
            retry_after = resp.json().get("retry_after", RETRY_AFTER_DEFAULT)
            logger.warning(f"Rate limited opening interview — waiting {retry_after}s")
            time.sleep(retry_after)
            # Retry once
            resp = requests.post(url, headers=headers, cookies=COOKIES, timeout=10)
        return resp.status_code in (200, 201)
    except Exception as e:
        logger.error(f"Error opening interview for {request_id}: {e}")
        return False


def find_interview_channel(user_id, retries=3, retry_delay=2):
    """
    Find the group-DM interview channel that was just opened for user_id.
    Retries up to `retries` times with `retry_delay` seconds between attempts
    in case the channel hasn't been created yet.
    Returns the channel_id string or None.
    """
    url = "https://discord.com/api/v9/users/@me/channels"
    headers = get_headers()
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, cookies=COOKIES, timeout=10)
            if resp.status_code == 429:
                retry_after = resp.json().get("retry_after", RETRY_AFTER_DEFAULT)
                time.sleep(retry_after)
                continue
            channels = resp.json()
            if not isinstance(channels, list):
                return None
            for ch in channels:
                if isinstance(ch, dict) and ch.get("type") == 3:
                    recipient_ids = [u["id"] for u in ch.get("recipients", [])]
                    if str(user_id) in [str(r) for r in recipient_ids]:
                        return ch["id"]
        except Exception as e:
            logger.error(f"Error finding interview channel for user {user_id}: {e}")
            return None
        # Channel not found yet — wait and retry
        if attempt < retries - 1:
            time.sleep(retry_delay)
    return None


def send_message(channel_id, message):
    """Send a plain-text message to a channel."""
    headers = get_headers()
    headers["referer"] = f"https://discord.com/channels/@me/{channel_id}"
    headers["content-type"] = "application/json"
    data = {
        "content": message,
        "nonce": str(random.randint(10**17, 10**18 - 1)),
        "tts": False,
        "flags": 0,
    }
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    try:
        resp = requests.post(url, headers=headers, cookies=COOKIES,
                             data=json.dumps(data), timeout=10)
        if resp.status_code in (200, 201):
            return True
        if resp.status_code == 429:
            retry_after = resp.json().get("retry_after", 10)
            logger.warning(f"Rate limited sending message — waiting {retry_after}s")
            time.sleep(retry_after)
            # Retry once after the rate-limit clears
            resp = requests.post(url, headers=headers, cookies=COOKIES,
                                 data=json.dumps(data), timeout=10)
            if resp.status_code in (200, 201):
                return True
            logger.warning(f"Failed to send message on retry. Status: {resp.status_code}")
        else:
            logger.warning(
                f"Failed to send message. Status: {resp.status_code}"
            )
    except Exception as e:
        logger.error(f"Exception sending message: {e}")
    return False


def main():
    if not TOKEN:
        logger.error("TOKEN is not set. Edit the TOKEN variable in open_pending_apps.py or set the DISCORD_TOKEN environment variable.")
        sys.exit(1)

    # Allow an optional custom message as CLI argument
    message = sys.argv[1] if len(sys.argv) > 1 else AUTH_REQUEST_MESSAGE

    logger.info("Fetching pending applications…")
    applications = get_pending_applications()

    if not applications:
        logger.info("No pending applications found.")
        return

    total = len(applications)
    logger.info(f"Found {total} pending application(s). Opening one by one…")

    for idx, app in enumerate(applications, start=1):
        request_id = app.get("id") or app.get("request_id")
        user = app.get("user") or {}
        user_id = user.get("id") or app.get("user_id")

        if not request_id or not user_id:
            logger.warning(f"[{idx}/{total}] Skipping — missing request_id or user_id: {app}")
            continue

        logger.info(f"[{idx}/{total}] Opening interview for user {user_id} (request {request_id})…")

        # 1. Open the interview
        if not open_interview(request_id):
            logger.warning(f"[{idx}/{total}] Failed to open interview — skipping user {user_id}")
            time.sleep(DELAY_BETWEEN_APPS)
            continue

        # 2. Wait for Discord to create the channel
        time.sleep(CHANNEL_CREATION_WAIT)

        # 3. Find the newly created interview channel
        channel_id = find_interview_channel(user_id)
        if not channel_id:
            logger.warning(f"[{idx}/{total}] Could not find channel for user {user_id}")
            time.sleep(DELAY_BETWEEN_APPS)
            continue

        # 4. Send the message
        if send_message(channel_id, message):
            logger.info(f"[{idx}/{total}] ✅ Message sent to channel {channel_id}")
        else:
            logger.warning(f"[{idx}/{total}] Message send failed for channel {channel_id}")

        # 5. Moderate delay before next application
        if idx < total:
            time.sleep(DELAY_BETWEEN_APPS)

    logger.info("Done — all pending applications processed.")


if __name__ == "__main__":
    main()
