import os
import time
import configparser
import discord
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogFileHandler(FileSystemEventHandler):
    """Custom event handler for monitoring log files."""

    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    def on_modified(self, event):
        if event.src_path.endswith(tuple(LOG_FILENAMES)):
            with open(event.src_path, "r") as f:
                last_line = f.readlines()[-1].strip()
                self.bot.loop.create_task(self.channel.send(last_line))


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = None

    async def on_ready(self):
        print(f"Logged in as {self.user} | krezioo")
        self.channel = self.get_channel(CHANNEL_ID)
        event_handler = LogFileHandler(self, self.channel)
        observer = Observer()
        for filename in LOG_FILENAMES:
            observer.schedule(event_handler, os.path.dirname(filename), recursive=False)
        observer.start()
        print(f"Monitoring {LOG_FILENAMES} for changes...")

    async def on_error(self, event, *args, **kwargs):
        print(f"Error: {event}")
        await super().on_error(event, *args, **kwargs)


# Load configuration from file
config = configparser.ConfigParser()
config.read("config.ini")

TOKEN = config.get("discord", "token")
CHANNEL_ID = int(config.get("discord", "channel_id"))
LOG_FILENAMES = config.get("app", "log_filenames").split(",")

bot = Bot(command_prefix="!")
bot.run(TOKEN)