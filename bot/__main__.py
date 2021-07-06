import shutil, psutil
import signal
import os

from pyrogram import idle
from bot import app
from sys import executable
from datetime import datetime
import pytz
import time

from telegram import ParseMode, BotCommand
from telegram.ext import CommandHandler
from bot import bot, dispatcher, updater, botStartTime, IMAGE_URL, IGNORE_PENDING_REQUESTS
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, search, delete, speedtest, usage, mediainfo, count, config, updates

now=datetime.now(pytz.timezone('Asia/Kolkata'))


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime('%Y/%m/%d %I:%M:%S %p')
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'𝐁𝐨𝐭 𝐔𝐩𝐭𝐢𝐦𝐞: {currentTime}\n' \
            f'𝐒𝐭𝐚𝐫𝐭 𝐓𝐢𝐦𝐞: {current}\n' \
            f'𝐓𝐨𝐭𝐚𝐥 𝐃𝐢𝐬𝐤 𝐒𝐩𝐚𝐜𝐞: {total}\n' \
            f'𝐔𝐬𝐞𝐝: {used}  ' \
            f'𝐅𝐫𝐞𝐞: {free}\n\n' \
            f'📊𝐃𝐚𝐭𝐚 𝐔𝐬𝐚𝐠𝐞📊\n𝐔𝐩𝐥𝐨𝐚𝐝: {sent}\n' \
            f'𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝: {recv}\n\n' \
            f'𝐂𝐏𝐔: {cpuUsage}%\n' \
            f'𝐑𝐀𝐌: {memory}%\n' \
            f'𝐃𝐈𝐒𝐊: {disk}%'
    sendMessage(stats, context.bot, update)


def start(update, context):
    start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Mirror Group", "https://t.me/WeNubMirrors")
    buttons.buildbutton("We◉NúbGang", "https://t.me/WeNubGang")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince: <code>{uptime}</code>", context.bot, update)
        else :
            update.effective_message.reply_photo(IMAGE_URL, start_string, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else :
        sendMessage(f"Oops! not a Authorized user.", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive.

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.CloneCommand}: Copy file/folder to Google Drive

/{BotCommands.CountCommand}: Count file/folder of Google Drive Links

/{BotCommands.DeleteCommand} [link]: Delete file from Google Drive (Only Owner & Sudo)

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, if found replies with the link

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner)

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.ConfigMenuCommand}: Get Info Menu about bot config (Owner Only).

/{BotCommands.UpdateCommand}: Update Bot from Upstream Repo. (Owner Only).

/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner & Sudo only).

/{BotCommands.SpeedCommand}: Check Internet Speed of the Host

/{BotCommands.MediaInfoCommand}: Get detailed info about replied media (Only for Telegram file).

/{BotCommands.ShellCommand}: Run commands in Shell (Terminal).

/tshelpml: Get help for Torrent search module.
'''

    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive.

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.CloneCommand}: Copy file/folder to Google Drive

/{BotCommands.CountCommand}: Count file/folder of Google Drive Links

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, if found replies with the link

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.SpeedCommand}: Check Internet Speed of the Host

/{BotCommands.MediaInfoCommand}: Get detailed info about replied media (Only for Telegram file).

/tshelpml: Get help for Torrent search module.
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
BotCommand(f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
BotCommand(f'{BotCommands.TarMirrorCommand}','Upload tar (zipped) file'),
BotCommand(f'{BotCommands.UnzipMirrorCommand}','Extract files'),
BotCommand(f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
BotCommand(f'{BotCommands.WatchCommand}','Mirror YT-DL support link'),
BotCommand(f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as tar'),
BotCommand(f'{BotCommands.StatusCommand}','Get Mirror Status message')]


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    sendMessage(f"Bot Booted Successfully!", context.bot, update)
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
