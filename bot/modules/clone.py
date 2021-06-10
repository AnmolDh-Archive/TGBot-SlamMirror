from telegram.ext import CommandHandler, run_async
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMarkup, deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import dispatcher, CLONE_LIMIT, STOP_DUPLICATE_CLONE
from bot.helper.ext_utils.bot_utils import get_readable_file_size


@run_async
def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        gd = GoogleDriveHelper()
        if CLONE_LIMIT is not None or STOP_DUPLICATE_CLONE:
            msg1 = sendMessage(f"Checking Your Link...", context.bot, update)
            res, clonesize, name = gd.clonehelper(link)
            if res != "":
               deleteMessage(context.bot, msg1)
               sendMessage(res, context.bot, update)
               return
        if STOP_DUPLICATE_CLONE:
            smsg, button = gd.drive_list(name)
            if smsg:
                deleteMessage(context.bot, msg1)
                msg3 = "<b>File/Folder is already available in Drive</b>.\n<b>Here are the search results:</b>"
                sendMarkup(msg3, context.bot, update, button)
                return
            else:
                if CLONE_LIMIT is None:
                    deleteMessage(context.bot, msg1)
        if CLONE_LIMIT is not None:
            limit = CLONE_LIMIT
            limit = limit.split(' ', maxsplit=1)
            limitint = int(limit[0])
            msg2 = f'Failed, Clone limit is {CLONE_LIMIT}.\nYour File/Folder size is {get_readable_file_size(clonesize)}.'
            if 'GB' in limit or 'gb' in limit:
                if clonesize > limitint * 1024**3:
                    deleteMessage(context.bot, msg1)
                    sendMessage(msg2, context.bot, update)
                    return
                else:
                    deleteMessage(context.bot, msg1)
            elif 'TB' in limit or 'tb' in limit:
                if clonesize > limitint * 1024**4:
                    deleteMessage(context.bot, msg1)
                    sendMessage(msg2, context.bot, update)
                    return
                else:
                    deleteMessage(context.bot, msg1)                
        msg = sendMessage(f"Cloning: <code>{link}</code>", context.bot, update)
        result, button = gd.clone(link)
        deleteMessage(context.bot, msg)
        if button == "":
            sendMessage(result, context.bot, update)
        else:
            if update.message.from_user.username:
                uname = f'@{update.message.from_user.username}'
            else:
                uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            if uname is not None:
                cc = f'\n\n𝐔𝐩𝐥𝐨𝐚𝐝𝐞𝐫: <i>{uname}</i>'
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('Provide G-Drive Shareable Link to Clone.', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(clone_handler)
