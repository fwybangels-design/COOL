# Paste-Based DM Retry Feature

## Overview

This feature allows you to paste logs from previous DM operations and retry DMing users with **strict bot-user pairing**. Each bot will only DM the users it has previously DMed.

## How It Works

### 1. Paste Your Logs

In the Re-Mass DM Control Panel, there's a text area labeled "Paste DM Logs (Optional)". You can paste logs in this format:

```
catgirl paws#8286  Attempting to DM dove76 (1467251209617281065)... Success!
sophi#2614  Attempting to DM theconcubine (1318780688748642396)... Success!
lia#3112  Attempting to DM fuckesluts (1462979766473986141)... Failed: 403 Forbidden
sese#1003  Attempting to DM 7.92x77 (1446761824493240331)... Success!
catboss eva#7036  Attempting to DM afraid222222 (1259765734150504519)... Success!
```

### 2. Strict Bot-User Pairing

The system will:
- ✅ Parse the logs to extract bot names and user IDs
- ✅ Match each bot name to available tokens
- ✅ Each bot will ONLY DM users it has previously DMed
- ✅ User IDs from bots without tokens are SKIPPED
- ✅ No cross-contamination between bots

### 3. Example Scenario

**Pasted Logs:**
```
bot1#1234  Attempting to DM user_a (111...)... Success!
bot1#1234  Attempting to DM user_b (222...)... Success!
bot2#5678  Attempting to DM user_c (333...)... Success!
bot3#9999  Attempting to DM user_d (444...)... Success!
```

**Available Tokens:**
- bot1#1234 ✓
- bot2#5678 ✓

**Result:**
- `bot1#1234` will DM: user_a, user_b (2 users)
- `bot2#5678` will DM: user_c (1 user)
- `bot3#9999` SKIPPED (no token) - user_d will NOT be DMed
- **Total: 3 users will be DMed**

## Key Features

### Handles Large Pastes
You can paste logs with many different bots. The system will:
- Parse all bots and their associated users
- Only use bots that have matching tokens
- Skip bots without tokens
- Log which bots are matched and which are skipped

### Maintains History
Each bot maintains its own user list from the logs:
- Bot A only DMs Bot A's users
- Bot B only DMs Bot B's users
- No mixing of user lists between bots

### Clear Logging
The system provides detailed logs:
```
Available bot tokens (2): ['bot1#1234', 'bot2#5678']
Bots found in pasted logs (3): ['bot1#1234', 'bot2#5678', 'bot3#9999']
✓ Matched 'bot1#1234' → will DM 2 users
✓ Matched 'bot2#5678' → will DM 1 users
✗ No token for 'bot3#9999' → skipping 1 users
SKIPPED: 1 bots with 1 total users (no matching tokens)
✓ READY: 2 bots will DM 3 users total
```

## Supported Log Formats

The parser supports multiple formats:

### Basic Format
```
botname#disc  Attempting to DM username (user_id)... Success!
```

### With Wave Prefix
```
[Initial] botname#disc  Attempting to DM username (user_id)... Success!
[Wave_1] botname#disc  Attempting to DM username (user_id)... Failed
```

### Without Discriminator (for new Discord usernames)
```
botname  Attempting to DM username (user_id)... Success!
```

### Mixed Success/Failure
Both successful and failed DMs are parsed:
```
bot#1234  Attempting to DM user1 (111...)... Success!
bot#1234  Attempting to DM user2 (222...)... Failed: 403 Forbidden (error code: 50007): Cannot send messages to this user
```

## Usage Steps

1. **Add Bot Tokens**: Add your bot tokens in the "Bot Tokens" section
2. **Enter Message**: Enter the message to send (or leave default)
3. **Paste Logs**: Paste your previous DM logs in the "Paste DM Logs" section
4. **Click START**: The system will:
   - Parse the logs
   - Match bots to tokens
   - Show which bots will be used
   - DM users with strict pairing
5. **Monitor Logs**: Watch the live logs to see progress

## Normal Mode vs Paste Mode

### Normal Mode (no paste)
- Scans bots' DM channels
- Distributes all found users evenly across all bots
- Good for re-DMing everyone

### Paste Mode (with pasted logs)
- Uses pasted bot-user pairings
- Each bot only DMs its assigned users
- Good for retrying specific pairings

## Important Notes

⚠️ **Bot Name Matching**: The bot usernames/discriminators in your tokens must match the names in the pasted logs for matching to work.

⚠️ **Unmatched Bots**: If a bot from the logs doesn't have a matching token, its users will be skipped (not redistributed to other bots).

✅ **Safe**: This ensures you never accidentally DM users with the wrong bot.

## Example Use Case

You ran a mass DM operation yesterday and saved the logs. Today you want to retry DMing the same users with the same bots:

1. Open the control panel
2. Add your bot tokens
3. Paste yesterday's logs
4. Click START
5. Each bot will retry only the users it DMed yesterday

This maintains consistency and prevents confusion about which bot DMed which user.
