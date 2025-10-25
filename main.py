SCHEDULER_TASKS = {}
from typing import Final
from dotenv import load_dotenv
from nextcord import Intents, Client, Embed
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, CheckFailure
import os, datetime, asyncio, nextcord, subprocess
from datetime import datetime, timedelta
import json
import sys
import webserver
from zoneinfo import ZoneInfo
import firebase_db

# Funzione per inviare gli eventi in batch di 10 per messaggio, ogni embed contiene 10 eventi formattati come richiesto
async def send_upcoming_events(channel):
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            await channel.send(f"❌ Error fetching events: {result.stderr[:1000]}")
            return
        try:
            events = json.loads(result.stdout.strip())
        except Exception:
            # Fallback: riga per riga
            events = []
            for line in result.stdout.splitlines():
                if line.strip():
                    try:
                        evt = json.loads(line)
                        events.append(evt)
                    except Exception:
                        pass
        today = datetime.now().strftime("%Y-%m-%d")
        if not events:
            await channel.send(f"📢 No upcoming CTF events found (as of {today}).")
            return

        def calculate_duration(start_end_str):
            try:
                if '—' in start_end_str:
                    start_str, end_str = start_end_str.split('—')
                    start_str = start_str.strip().replace('.', '')
                    end_str = end_str.strip().replace('.', '')
                    import re
                    year_match = re.search(r'(\d{4})', end_str)
                    year = year_match.group(1) if year_match else None
                    try:
                        end_time = datetime.strptime(end_str, "%d %B %Y, %H:%M UTC")
                        start_time = datetime.strptime(f"{start_str} {year}", "%d %B, %H:%M UTC %Y")
                    except Exception:
                        try:
                            end_time = datetime.strptime(end_str, "%d %b %Y, %H:%M UTC")
                            start_time = datetime.strptime(f"{start_str} {year}", "%d %b, %H:%M UTC %Y")
                        except Exception:
                            return None
                    duration = end_time - start_time
                    return duration.total_seconds() / 3600
                return None
            except Exception:
                return None

        batch_size = 10
        total_pages = (len(events) + batch_size - 1) // batch_size
        for page_num, i in enumerate(range(0, len(events), batch_size), start=1):
            group = events[i:i+batch_size]
            description = ""
            for event in group:
                if len(event) >= 4:
                    duration_hours = calculate_duration(event[1])
                    duration_str = f"{duration_hours:.0f} hours" if duration_hours is not None else "Duration not available"
                    description += (
                        f"**[{event[0]}](https://ctftime.org{event[3]})**\n"
                        f"📅 **Date:** {event[1]}\n"
                        f"⚔️ **Format:** {event[2]}\n"
                        f"⏱️ **Duration:** {duration_str}\n\n"
                    )
                else:
                    description += f"{event}\n\n"
            embed = Embed(title="Upcoming CTF Events", description=description[:4096], color=0x3498db)
            embed.set_footer(text=f"Page {page_num}/{total_pages}")
            await channel.send(embed=embed)
    except Exception as e:
        await channel.send(f"❌ Errore durante l'invio degli eventi: {e}")

# Load environment variables from a .env file
load_dotenv()


# Define a constant for the Discord bot token, retrieved from environment variables
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Define default intents for the bot
intents: Intents = Intents.default()

# Enable the message content intent, necessary to read message content
intents.message_content = True

# Initialize the client with the specified intents
bot = commands.Bot(command_prefix='/', intents=intents)


# Get the base directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the bot's icon image
icon_path = os.path.join(BASE_DIR, 'bot_ctf_time_icon.png')

# Construct the full path to the upcoming events script
script_path = os.path.join(BASE_DIR, 'upcoming_events.py')


@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is running!')
    
    # Inizializza Firebase
    try:
        firebase_db.init_firebase()
        print("✅ Firebase connected successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print("⚠️ Bot will not work properly without Firebase!")
        return
    
    if os.path.exists(icon_path):
        with open(icon_path, 'rb') as f:
            avatar_image = f.read()
        try:
            await bot.user.edit(avatar=avatar_image)
        except Exception as e:
            print(f"Failed to set bot avatar: {e}")

    # Avvia una scheduling task per ogni server configurato
    try:
        configs = firebase_db.get_all_configs()
        for guild_id, conf in configs.items():
            if conf.get("channel_id"):
                if str(guild_id) not in SCHEDULER_TASKS or SCHEDULER_TASKS[str(guild_id)] is None or SCHEDULER_TASKS[str(guild_id)].done():
                    print(f"[AUTO-SCHEDULER] Avvio scheduling task per guild {guild_id}")
                    SCHEDULER_TASKS[str(guild_id)] = bot.loop.create_task(schedule_daily_message_multi(str(guild_id)))
    except Exception as e:
        print(f"[AUTO-SCHEDULER] Errore durante l'avvio automatico delle scheduling task: {e}")


def calculate_duration(start_end_str):
    try:
        start_str, end_str = start_end_str.split(" — ")

        # Normalize: remove dots for compatibility with %b and %B
        start_str = start_str.replace(".", "")
        end_str = end_str.replace(".", "")

        # Try first with %B (extended form like "August")
        try:
            end_time = datetime.strptime(end_str, "%d %B %Y, %H:%M UTC")
            start_str_with_year = f"{start_str} {end_time.year}"
            start_time = datetime.strptime(start_str_with_year, "%d %B, %H:%M UTC %Y")
        except ValueError:
            # Fallback with %b (short form like "Aug")
            end_time = datetime.strptime(end_str, "%d %b %Y, %H:%M UTC")
            start_str_with_year = f"{start_str} {end_time.year}"
            start_time = datetime.strptime(start_str_with_year, "%d %b, %H:%M UTC %Y")

        duration = end_time - start_time
        return duration.total_seconds() / 3600
    except Exception as e:
        print(f"Error calculating duration: {e}")
        return None

@bot.command(name="set_schedule_channel")
async def set_schedule_channel(ctx):
    guild_id = str(ctx.guild.id)
    channel_id = ctx.channel.id
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if guild_config.get("channel_id") == channel_id:
            await ctx.send(f"⚠️ This channel (`#{ctx.channel.name}`) is already set for daily scheduled messages.")
            return
        
        guild_config["channel_id"] = channel_id
        # Default time and timezone if not set
        guild_config.setdefault("hour", 0)
        guild_config.setdefault("minute", 0)
        guild_config.setdefault("timezone", "Europe/Rome")
        
        firebase_db.save_guild_config(guild_id, guild_config)
        
        await ctx.send(f"✅ This channel (`#{ctx.channel.name}`) has been set for daily scheduled messages.")
        # Riavvia sempre lo scheduler per questa guild
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
    except Exception as e:
        await ctx.send("❌ Failed to save the channel.")
        print(f"Error saving scheduled channel: {e}")

@bot.command(name="unset_schedule_channel")
async def unset_schedule_channel(ctx):
    guild_id = str(ctx.guild.id)
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("⚠️ No scheduled channel was set.")
            return
            
        firebase_db.delete_guild_field(guild_id, "channel_id")
        
        await ctx.send("✅ The scheduled channel has been unset successfully.")
        # Stop scheduler for this guild if running
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS.pop(guild_id, None)
    except Exception as e:
        await ctx.send("❌ Failed to unset the scheduled channel.")
        print(f"Error unsetting scheduled channel: {e}")

@bot.command(name="schedule_status")
async def schedule_status(ctx):
    try:
        guild_id = str(ctx.guild.id)
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("❌ Not configured. Use `/set_schedule_channel` to set up daily messages")
            return
            
        channel_id = guild_config["channel_id"]
        schedule_hour = guild_config.get("hour", 0)
        schedule_minute = guild_config.get("minute", 0)
        timezone_name = guild_config.get("timezone", "Europe/Rome")
        user_tz = ZoneInfo(timezone_name)
        channel = bot.get_channel(channel_id)
        now = datetime.now(user_tz)
        then = now.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
        if then <= now:
            then += timedelta(days=1)
        wait_time = (then - now).total_seconds()
        hours_until = wait_time / 3600
        if channel:
            embed = Embed(
                title="📅 Scheduler Status",
                description=f"✅ **Active**\n📍 **Channel:** {channel.mention}\n🌍 **Timezone:** {timezone_name}\n🕐 **Current time:** {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n⏰ **Scheduled time:** {schedule_hour:02d}:{schedule_minute:02d} (daily)\n⏱️ **Next message:** in {hours_until:.1f} hours at {then.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                color=0x00ff00
            )
        else:
            embed = Embed(
                title="📅 Scheduler Status",
                description=f"❌ **Channel not found**\nChannel ID: {channel_id}\nPlease reset the channel with `/set_schedule_channel`",
                color=0xff0000
            )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error checking scheduler status: {e}")

@bot.command(name="test_schedule")
@has_permissions(administrator=True)
async def test_schedule(ctx):
    try:
        guild_id = str(ctx.guild.id)
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("❌ No scheduled channel configured. Use `/set_schedule_channel` first.")
            return
            
        channel_id = guild_config["channel_id"]
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send(f"❌ Channel with ID {channel_id} not found. Please reset the channel with `/set_schedule_channel`.")
            return
        await ctx.send(f"🧪 Testing scheduled message in {channel.mention}...")
        try:
            await send_upcoming_events(channel)
        except Exception as send_error:
            await ctx.send(f"❌ Error sending test message: {send_error}")
    except Exception as e:
        await ctx.send(f"❌ Error checking scheduler status: {e}")

async def schedule_daily_message_multi(guild_id):
    SCHEDULER_TASKS[str(guild_id)] = asyncio.current_task()
    try:
        while True:
            try:
                # Carica la configurazione aggiornata
                guild_config = firebase_db.get_guild_config(str(guild_id))
                
                if not guild_config or "channel_id" not in guild_config:
                    await asyncio.sleep(3600)
                    continue
                    
                channel_id = guild_config["channel_id"]
                schedule_hour = guild_config.get("hour", 0)
                schedule_minute = guild_config.get("minute", 0)
                timezone_name = guild_config.get("timezone", "Europe/Rome")
                user_tz = ZoneInfo(timezone_name)
                channel = bot.get_channel(channel_id)
                if not channel:
                    await asyncio.sleep(3600)
                    continue
                now = datetime.now(user_tz)
                then = now.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
                if then <= now:
                    then += timedelta(days=1)
                wait_time = (then - now).total_seconds()
                if wait_time < 30:
                    wait_time = 60
                if wait_time > 120:
                    sleep_intervals = int(wait_time // 60)
                    remainder = wait_time % 60
                    for _ in range(sleep_intervals):
                        await asyncio.sleep(60)
                    if remainder > 0:
                        await asyncio.sleep(remainder)
                else:
                    await asyncio.sleep(wait_time)
                try:
                    await channel.purge(limit=None)
                    await send_upcoming_events(channel)
                except Exception as send_error:
                    try:
                        await send_upcoming_events(channel)
                    except Exception as fallback_error:
                        print(f"[SCHEDULER][{guild_id}] Fallback send also failed: {fallback_error}")
            except asyncio.CancelledError:
                print(f"[SCHEDULER][{guild_id}] Task cancelled.")
                break
            except Exception as e:
                print(f"[SCHEDULER][{guild_id}] Error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(3600)
    finally:
        SCHEDULER_TASKS.pop(str(guild_id), None)

@bot.command(name="list_timezones")
# Shows a list of available timezones. Usage: /list_timezones [region]
async def list_timezones(ctx, region: str = None):
    try:
        # List of common timezones divided by region
        all_timezones = {
            "Europe": [
                "Europe/Rome", "Europe/London", "Europe/Paris", "Europe/Berlin", 
                "Europe/Madrid", "Europe/Amsterdam", "Europe/Brussels", "Europe/Vienna",
                "Europe/Prague", "Europe/Warsaw", "Europe/Stockholm", "Europe/Oslo",
                "Europe/Copenhagen", "Europe/Helsinki", "Europe/Dublin", "Europe/Lisbon",
                "Europe/Athens", "Europe/Budapest", "Europe/Bucharest", "Europe/Sofia"
            ],
            "America": [
                "America/New_York", "America/Los_Angeles", "America/Chicago", "America/Denver",
                "America/Phoenix", "America/Toronto", "America/Vancouver", "America/Montreal",
                "America/Mexico_City", "America/Sao_Paulo", "America/Buenos_Aires", "America/Lima",
                "America/Bogota", "America/Santiago", "America/Caracas", "America/La_Paz",
                "America/Montevideo", "America/Asuncion", "America/Havana", "America/Jamaica"
            ],
            "Asia": [
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Seoul", "Asia/Hong_Kong",
                "Asia/Singapore", "Asia/Bangkok", "Asia/Jakarta", "Asia/Manila",
                "Asia/Kuala_Lumpur", "Asia/Taipei", "Asia/Mumbai", "Asia/Kolkata",
                "Asia/Delhi", "Asia/Karachi", "Asia/Dubai", "Asia/Tehran",
                "Asia/Baghdad", "Asia/Riyadh", "Asia/Jerusalem", "Asia/Beirut"
            ],
            "Australia": [
                "Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane", "Australia/Perth",
                "Australia/Adelaide", "Australia/Darwin", "Australia/Hobart", "Pacific/Auckland",
                "Pacific/Fiji", "Pacific/Tahiti", "Pacific/Honolulu", "Pacific/Guam"
            ],
            "Africa": [
                "Africa/Cairo", "Africa/Lagos", "Africa/Nairobi", "Africa/Johannesburg",
                "Africa/Casablanca", "Africa/Algiers", "Africa/Tunis", "Africa/Accra",
                "Africa/Kinshasa", "Africa/Addis_Ababa", "Africa/Dar_es_Salaam", "Africa/Harare"
            ]
        }
        
        if region:
            # Filter by specific region
            region_key = region.capitalize()
            if region_key not in all_timezones:
                await ctx.send(f"❌ No timezones found for region '{region}'.\n**Available regions:** Europe, America, Asia, Africa, Australia")
                return
            
            filtered_timezones = all_timezones[region_key]
            
            description = f"**Timezones for {region_key}:**\n"
            for tz in filtered_timezones:
                description += f"• {tz}\n"
                
        else:
            # Show some popular timezones
            popular_timezones = [
                "Europe/Rome", "Europe/London", "Europe/Paris", "Europe/Berlin",
                "America/New_York", "America/Los_Angeles", "America/Chicago",
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Mumbai",
                "Australia/Sydney", "Africa/Cairo", "Pacific/Auckland"
            ]
            
            description = "**Popular timezones:**\n"
            for tz in popular_timezones:
                try:
                    current_time = datetime.now(ZoneInfo(tz))
                    description += f"• {tz} - {current_time.strftime('%H:%M %Z')}\n"
                except:
                    description += f"• {tz}\n"
            
            description += "\n**To see all timezones for a region:**\n`/list_timezones Europe`, `/list_timezones America`, etc."
        
        embed = Embed(
            title="🌍 Available Timezones",
            description=description,
            color=0x2ecc71
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error retrieving timezones: {e}")


# Set the schedule time for this guild
@bot.command(name="set_schedule_time")
async def set_schedule_time(ctx, hour: int, minute: int = 0):
    guild_id = str(ctx.guild.id)
    try:
        if not (0 <= hour < 24 and 0 <= minute < 60):
            await ctx.send("❌ Invalid time. Hour must be 0-23 and minute 0-59.")
            return
        
        guild_config = firebase_db.get_guild_config(guild_id)
        guild_config["hour"] = hour
        guild_config["minute"] = minute
        firebase_db.save_guild_config(guild_id, guild_config)
        
        await ctx.send(f"✅ Scheduled time set to {hour:02d}:{minute:02d} (24h format) for this server.")
        # Restart scheduler for this guild
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
    except Exception as e:
        await ctx.send(f"❌ Error setting schedule time: {e}")

# Get the schedule time for this guild
@bot.command(name="get_schedule_time")
async def get_schedule_time(ctx):
    guild_id = str(ctx.guild.id)
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "hour" not in guild_config:
            await ctx.send("❌ No scheduled time configured. Use `/set_schedule_time` first.")
            return
            
        hour = guild_config.get("hour", 0)
        minute = guild_config.get("minute", 0)
        await ctx.send(f"⏰ Scheduled time for this server: {hour:02d}:{minute:02d} (24h format)")
    except Exception as e:
        await ctx.send(f"❌ Error retrieving schedule time: {e}")

# Reset the schedule time to midnight for this guild
@bot.command(name="reset_schedule_time")
async def reset_schedule_time(ctx):
    guild_id = str(ctx.guild.id)
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        guild_config["hour"] = 0
        guild_config["minute"] = 0
        firebase_db.save_guild_config(guild_id, guild_config)
        
        await ctx.send("✅ Scheduled time reset to 00:00 (midnight) for this server.")
        # Restart scheduler for this guild
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
    except Exception as e:
        await ctx.send(f"❌ Error resetting schedule time: {e}")

# Set the timezone for this guild
@bot.command(name="set_timezone")
async def set_timezone(ctx, timezone: str):
    guild_id = str(ctx.guild.id)
    try:
        # Validate timezone
        try:
            tz = ZoneInfo(timezone)
        except Exception:
            await ctx.send(f"❌ Invalid timezone: {timezone}\nUse `/list_timezones` to see available options.")
            return
        
        guild_config = firebase_db.get_guild_config(guild_id)
        guild_config["timezone"] = timezone
        firebase_db.save_guild_config(guild_id, guild_config)
        
        current_time = datetime.now(tz)
        await ctx.send(f"✅ Timezone set to **{timezone}**\n🕐 **Current time:** {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        # Restart scheduler for this guild
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
    except Exception as e:
        await ctx.send(f"❌ Error setting timezone: {e}")

# Get the timezone for this guild
@bot.command(name="get_timezone")
async def get_timezone(ctx):
    guild_id = str(ctx.guild.id)
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        timezone_name = guild_config.get("timezone", "Europe/Rome") if guild_config else "Europe/Rome"
        tz = ZoneInfo(timezone_name)
        current_time = datetime.now(tz)
        await ctx.send(f"🌍 Timezone for this server: **{timezone_name}**\n🕐 **Current time:** {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    except Exception as e:
        await ctx.send(f"❌ Error retrieving timezone: {e}")

# Reset the timezone to default (Europe/Rome) for this guild
@bot.command(name="reset_timezone")
async def reset_timezone(ctx):
    guild_id = str(ctx.guild.id)
    try:
        guild_config = firebase_db.get_guild_config(guild_id)
        guild_config["timezone"] = "Europe/Rome"
        firebase_db.save_guild_config(guild_id, guild_config)
        
        italy_tz = ZoneInfo('Europe/Rome')
        current_time = datetime.now(italy_tz)
        await ctx.send(f"✅ Timezone reset to **Europe/Rome** (Italy)\n🕐 **Current time:** {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        # Restart scheduler for this guild
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            task.cancel()
            await asyncio.sleep(1)
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
    except Exception as e:
        await ctx.send("❌ Error resetting timezone.")
        print(f"Error resetting timezone: {e}")


@bot.command(name="debug")
@has_permissions(administrator=True)
async def debug(ctx):
    # Debug command to check bot status (multi-server aware).
    try:
        debug_info = []
        guild_id = str(ctx.guild.id) if ctx.guild else None

        # Check per-guild configuration
        debug_info.append("**📁 Per-Guild Configuration (Firebase):**")
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if guild_config:
            channel_id = guild_config.get("channel_id")
            hour = guild_config.get("hour", 0)
            minute = guild_config.get("minute", 0)
            timezone_name = guild_config.get("timezone", "Europe/Rome")
            channel = bot.get_channel(channel_id) if channel_id else None
            debug_info.append(f"✅ Channel: {channel.mention if channel else f'ID {channel_id} (not found)'}") if channel_id else debug_info.append("❌ Channel: Not set")
            debug_info.append(f"⏰ Time: {hour:02d}:{minute:02d}")
            debug_info.append(f"🌍 Timezone: {timezone_name}")
        else:
            debug_info.append("❌ No configuration found for this server in Firebase")

        # Check if scheduling task is active for this guild (using global registry)
        debug_info.append("\n**🔄 Scheduling Task:**")
        task = SCHEDULER_TASKS.get(guild_id)
        if task and not task.done():
            debug_info.append("✅ Scheduling task is active for this server.")
        else:
            debug_info.append("❌ No active scheduling task for this server! Use `/restart_scheduler` if needed.")

        # Check external scripts
        debug_info.append("\n**🔧 External scripts:**")
        if os.path.exists(script_path):
            debug_info.append(f"✅ upcoming_events.py: Found")
            # Quick script test
            try:
                result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    debug_info.append("✅ upcoming_events.py: Works correctly")
                else:
                    debug_info.append(f"❌ upcoming_events.py: Error - {result.stderr[:100]}")
            except Exception as e:
                debug_info.append(f"❌ upcoming_events.py: Execution error - {str(e)[:100]}")
        else:
            debug_info.append(f"❌ upcoming_events.py: Not found at {script_path}")

        # Check timezone
        debug_info.append("\n**🌍 Timezone Test:**")
        try:
            tz = ZoneInfo('Europe/Rome')
            current_time = datetime.now(tz)
            debug_info.append(f"✅ ZoneInfo works: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        except Exception as e:
            debug_info.append(f"❌ ZoneInfo error: {e}")

        # Check bot permissions
        debug_info.append("\n**🤖 Bot Permissions:**")
        if ctx.guild:
            member = ctx.guild.get_member(bot.user.id)
            if member:
                perms = ctx.channel.permissions_for(member)
                debug_info.append(f"{'✅' if perms.send_messages else '❌'} Send Messages")
                debug_info.append(f"{'✅' if perms.manage_messages else '❌'} Manage Messages (for purge)")
                debug_info.append(f"{'✅' if perms.embed_links else '❌'} Embed Links")

        embed = Embed(
            title="🔍 Debug Information",
            description="\n".join(debug_info),
            color=0x3498db
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error during debug: {e}")

@debug.error
async def debug_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")


@bot.command(name="scheduler_logs")
@has_permissions(administrator=True)
async def scheduler_logs(ctx):
    # Shows detailed scheduler information (multi-server version).
    try:
        guild_id = str(ctx.guild.id)
        # Check if the scheduling task for this guild is still active (using global registry)
        task = SCHEDULER_TASKS.get(guild_id)
        info_lines = []
        info_lines.append(f"**🔄 Active Scheduling Task (this server):** {'1' if task and not task.done() else '0'}")
        if not task or task.done():
            info_lines.append("❌ **PROBLEM: No active scheduling task for this server!**")
            info_lines.append("⚠️ The bot may have crashed or frozen.")
            info_lines.append("💡 Use `/restart_scheduler` to fix the problem.")
        else:
            info_lines.append("✅ Scheduling task is active for this server")
        # Check current configuration
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            info_lines.append("❌ No scheduled channel configured for this server.")
            channel = None
            schedule_hour = 0
            schedule_minute = 0
            timezone_name = "Europe/Rome"
        else:
            channel_id = guild_config["channel_id"]
            channel = bot.get_channel(channel_id)
            schedule_hour = guild_config.get("hour", 0)
            schedule_minute = guild_config.get("minute", 0)
            timezone_name = guild_config.get("timezone", "Europe/Rome")
            if channel:
                info_lines.append(f"📍 **Target channel:** #{channel.name}")
            else:
                info_lines.append(f"❌ **Channel not found:** ID {channel_id}")
        # Calculate next message
        user_tz = ZoneInfo(timezone_name)
        now = datetime.now(user_tz)
        then = now.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
        if then <= now:
            then += timedelta(days=1)
        wait_time = (then - now).total_seconds()
        hours_until = wait_time / 3600
        info_lines.append(f"⏰ **Next message:** {then.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        info_lines.append(f"⏱️ **Time remaining:** {hours_until:.1f} hours ({wait_time:.0f} seconds)")
        embed = Embed(
            title="📊 Scheduler Status",
            description="\n".join(info_lines),
            color=0x3498db if task and not task.done() else 0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error checking scheduler: {e}")

@scheduler_logs.error
async def scheduler_logs_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")


@bot.command(name="force_schedule")
@has_permissions(administrator=True)
# Forces immediate sending of scheduled message (for testing), multi-server version.
async def force_schedule(ctx):
    try:
        guild_id = str(ctx.guild.id)
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("❌ No scheduled channel configured. Use `/set_schedule_channel` first.")
            return
            
        channel_id = guild_config["channel_id"]
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send(f"❌ Channel with ID {channel_id} not found. Please reset the channel with `/set_schedule_channel`.")
            return
        await ctx.send(f"🚀 Forcing scheduled message send to {channel.mention}...")
        # Try to purge messages if possible
        deleted_count = 0
        try:
            deleted_messages = await channel.purge(limit=None)
            deleted_count = len(deleted_messages)
        except Exception as purge_error:
            await ctx.send(f"⚠️ Could not delete messages: {purge_error}")
        try:
            await send_upcoming_events(channel)
            await ctx.send(f"✅ Message sent successfully!{' 🗑️ Deleted ' + str(deleted_count) + ' messages.' if deleted_count else ''}")
        except Exception as send_error:
            await ctx.send(f"❌ Error during sending: {send_error}")
            print(f"[FORCE_SCHEDULE] Error: {send_error}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
@bot.command(name="upcoming")
async def upcoming(ctx):
    """Shows upcoming CTF events (alias for /upcoming_events)."""
    try:
        await send_upcoming_events(ctx.channel)
    except Exception as e:
        await ctx.send(f"❌ Error showing upcoming events: {e}")

@bot.command(name="upcoming_events")
async def upcoming_events(ctx):
    """Shows upcoming CTF events."""
    try:
        await send_upcoming_events(ctx.channel)
    except Exception as e:
        await ctx.send(f"❌ Error showing upcoming events: {e}")

@force_schedule.error
async def force_schedule_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")


@bot.command(name="clear_channel")
@has_permissions(administrator=True)
# Clears all messages from the scheduled channel (multi-server version).
async def clear_channel(ctx):
    try:
        guild_id = str(ctx.guild.id)
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("❌ No scheduled channel configured. Use `/set_schedule_channel` first.")
            return
            
        channel_id = guild_config["channel_id"]
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send(f"❌ Channel with ID {channel_id} not found. Please reset the channel with `/set_schedule_channel`.")
            return
        await ctx.send(f"🗑️ Clearing all messages from {channel.mention}...")
        try:
            deleted_messages = await channel.purge(limit=None)
            await ctx.send(f"✅ Successfully deleted {len(deleted_messages)} messages from {channel.mention}!")
        except Exception as purge_error:
            await ctx.send(f"❌ Error during deletion: {purge_error}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@clear_channel.error
async def clear_channel_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")


@bot.command(name="restart_scheduler")
@has_permissions(administrator=True)
# Restarts the scheduling task (multi-server version, per-guild).
async def restart_scheduler(ctx):
    try:
        guild_id = str(ctx.guild.id)
        # Cancel existing scheduling task for this guild if present
        task = SCHEDULER_TASKS.get(guild_id)
        cancelled = 0
        if task and not task.done():
            task.cancel()
            cancelled = 1
        await ctx.send(f"🔄 Cancelled {cancelled} existing scheduling task for this server...")
        # Wait a moment to ensure task is cancelled
        await asyncio.sleep(1)
        # Restart the scheduling task for this guild
        SCHEDULER_TASKS[guild_id] = bot.loop.create_task(schedule_daily_message_multi(guild_id))
        await ctx.send("✅ Scheduling task restarted successfully!")
        # Show the new status
        await asyncio.sleep(2)
        await scheduler_logs(ctx)
    except Exception as e:
        await ctx.send(f"❌ Error restarting scheduler: {e}")

@restart_scheduler.error
async def restart_scheduler_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")


@bot.command(name="test_now")
@has_permissions(administrator=True)
async def test_now(ctx):
    # Tests immediate sending to configured channel without deleting messages (multi-server version).
    try:
        guild_id = str(ctx.guild.id)
        guild_config = firebase_db.get_guild_config(guild_id)
        
        if not guild_config or "channel_id" not in guild_config:
            await ctx.send("❌ No scheduled channel configured. Use `/set_schedule_channel` first.")
            return
            
        channel_id = guild_config["channel_id"]
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send(f"❌ Channel with ID {channel_id} not found. Please reset the channel with `/set_schedule_channel`.")
            return
        await ctx.send(f"🧪 Quick test sending to {channel.mention} (without deletion)...")
        try:
            await send_upcoming_events(channel)
            await ctx.send("✅ Test completed successfully!")
        except Exception as send_error:
            await ctx.send(f"❌ Error during test: {send_error}")
            print(f"[TEST_NOW] Error: {send_error}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@test_now.error
async def test_now_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("❌ Only administrators can use this command.")

@bot.command(name="help_ctf")
async def help_ctf(ctx):
    # Shows all available CTF bot commands.
    try:
        embed = Embed(
            title="🤖 CTF Time Bot Commands",
            description="Here are all available commands:",
            color=0x3498db
        )
        
        # Main commands
        embed.add_field(
            name="📢 **Main Commands**",
            value="`/upcoming` - Shows upcoming CTF events\n`/upcoming_events` - Alias for /upcoming",
            inline=False
        )

        # Scheduling configuration
        embed.add_field(
            name="⚙️ **Scheduling Configuration**",
            value="`/set_schedule_channel` - Set this channel for daily messages\n`/unset_schedule_channel` - Remove scheduled channel\n`/schedule_status` - Show scheduler status",
            inline=False
        )

        # Time management
        embed.add_field(
            name="🕐 **Time Management**",
            value="`/set_schedule_time <hour> [minute]` - Set time (e.g. `/set_schedule_time 8 30`)\n`/get_schedule_time` - Show current time\n`/reset_schedule_time` - Reset to midnight",
            inline=False
        )

        # Timezone management
        embed.add_field(
            name="🌍 **Timezone Management**",
            value="`/set_timezone <timezone>` - Set timezone (e.g. `/set_timezone Europe/Rome`)\n`/get_timezone` - Show current timezone\n`/list_timezones [region]` - List available timezones\n`/reset_timezone` - Reset to Europe/Rome",
            inline=False
        )

        # Admin commands
        embed.add_field(
            name="🔧 **Administrator Commands**",
            value="`/test_schedule` - Test scheduled sending\n`/force_schedule` - Force immediate sending\n`/test_now` - Quick test without deletion\n`/clear_channel` - Clear all messages\n`/debug` - Debug information\n`/scheduler_logs` - Scheduler status\n`/restart_scheduler` - Restart scheduler",
            inline=False
        )

        embed.set_footer(text="💡 Admin commands require administrator permissions")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error displaying help: {e}")

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    webserver.keep_alive()
    main()
