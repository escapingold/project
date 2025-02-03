import os
import re
import logging
import requests,json,logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler,CallbackContext, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from pymongo import MongoClient
import threading
from flask import Flask
from threading import Thread
from datetime import timedelta
import time
from colorama import Fore,init
from telegram.error import BadRequest
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)



#-----------------------------------------------------------------------------------

app = Flask('')
@app.route('/')
def home():
    return "I am alive"

def run_http_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    os.system("cls")

    t.start()
#---------------------------------------------------------------------------------------------------------------
#admin user ids
ADMIN_USER_ID= [8025763606]
#developer or channel owner id without @
owner="escapingold"

#channel username without @
channel="CosmicxCode"
#channel username with @
CHANNEL_USERNAME="@cosmicxcode"
#start image url
IMAGE_URL="https://drive.google.com/uc?export=download&id=12NpP98geZdW6dugFoZ4L_beaBgjpx96O"

#Bot token
BOT_TOKEN="7597310436:AAGFKMLj-UvEyp705AC1SyIo4HOVJ_-vEvI"

#channel to forward links
link_channel=-1002313840870

#channel for getting logs 
notification= -1002308562226

#---------------------------------------------------------------------------------------------------------------
#api url
API_URL = "https://terabox-player-apmf.onrender.com/generate" 
#----------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------#
MONGO_URI = "mongodb+srv://botplays90:botplays90@botplays.ycka9.mongodb.net/?retryWrites=true&w=majority&appName=botplays"
DB_NAME = "terabox_bot"
COLLECTION_NAME = "user_ids"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
#------------------------------------------------------------------------------------------------------------------------------------#

def load_user_ids():
    try:
        user_ids = [user["user_id"] for user in collection.find({}, {"_id": 0, "user_id": 1})]
        return user_ids
    except Exception as e:
        logger.error(f"Error loading user IDs from MongoDB: {e}")
        return []

def save_user_id(user_id):
    try:
        # Check if user_id already exists
        if collection.count_documents({"user_id": user_id}) == 0:
            collection.insert_one({"user_id": user_id})
            logger.info(f"User ID {user_id} saved to the database.")
        else:
            logger.info(f"User ID {user_id} already exists in the database.")
    except Exception as e:
        logger.error(f"Error saving user ID to MongoDB: {e}")

#----------------------------------------------------------------------------------------------------------------------------------------


def display():
    print(f"""
{Fore.LIGHTGREEN_EX}----------------------------------------------------------------------------------------
{Fore.LIGHTRED_EX} 🤖 Developer: {Fore.LIGHTYELLOW_EX} Ankush 
{Fore.LIGHTRED_EX} 📢 Telegram: {Fore.LIGHTYELLOW_EX} https://t.me/escapingold
{Fore.LIGHTRED_EX} 🌐 Channel: {Fore.LIGHTYELLOW_EX} https://t.me/cosmicxcode
{Fore.LIGHTGREEN_EX}----------------------------------------------------------------------------------------

{Fore.LIGHTCYAN_EX}Bot is Running⏳⏳⏳
    """)



VALID_URL_PATTERN = r"https?://(1024terabox|teraboxapp|terabox|terafileshareapp|terafileshare|teraboxlink|terasharelink)\.com/\S+"

START_TIME = time.time()



async def is_user_member_of_channel(context, user_id):
    try:
        # Check the membership status of the user in the channel
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        # Log the status to help debug
        logger.debug(f"User ID: {user_id}, Chat Member Status: {chat_member.status}")
        # If the user is a member, administrator, or the creator of the channel, return True
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        # Log the error to understand why the check failed
        logger.error(f"Error checking membership for user ID {user_id}: {e}")
        return False


async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name

    # Log the start of the function
    logger.debug(f"Start function triggered by user: {user_id} ({username})")

    # Check if the user is a member of the channel
    is_member = await is_user_member_of_channel(context, user_id)

    if not is_member:
        # User is not a member of the channel
        logger.debug(f"User {user_id} is not a member of the channel.")
        join_button_1 = InlineKeyboardButton("✳️ Join-channel", url=f"https://t.me/{channel}")        

        reply_markup = InlineKeyboardMarkup([
            [join_button_1]
        ])

        await update.message.reply_text(
            "⛔️ Please join our channel to use the bot! 🎥💨\n\n"
            "After join use /start to continue:",
            reply_markup=reply_markup
        )
        return  # Stop the rest of the code from executing if the user is not a member

    # If the user is a member, proceed with the rest of the function
    logger.debug(f"User {user_id} is a member of the channel.")

    # Save user id
    save_user_id(user_id)
    print("New user start bot:",user_id)

    # Notification message for the channel
    notify_message = (
        f"*📢 New user started the terabox!*\n\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"👤 *Username:* @{username}\n\n"
    )

    # Send the notification to your channel
    await context.bot.send_message(chat_id=notification, text=notify_message, parse_mode="MarkDown")

    # Welcome message
    welcome_text = (
        f"✨ Hey *{first_name}*\n"
        f"👤**User-Id= `{user_id}`\n\n"
        "Welcome to the **TeraBox & TeraShare Stream Bot** 🎬💖\n\n"
        "*Simply send me any TeraBox or TeraShare video link, and I'll instantly generate a direct streaming link for you*! 🎥💨\n\n"
        "*Need any help Contact 🤖Developer*!\n\n"
    )

    # Inline buttons
    keyboard = [
        [
            InlineKeyboardButton("🤖 Developer", url=f"https://t.me/{owner}"),
            InlineKeyboardButton("♻️ Channel", url=f"https://t.me/{channel}")
        ],
        [
            InlineKeyboardButton("❇️ Send Link", callback_data="send_link")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(photo=IMAGE_URL, caption=welcome_text, parse_mode="MarkDown", reply_markup=reply_markup)


async def send_link_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query
    await query.message.reply_text(
        "❗Please send your *TeraBox* or *TeraShare* video link here! 🚀🎥", 
        parse_mode="Markdown"
    )

async def send_uptime(update: Update, context: CallbackContext) -> None:
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(timedelta(seconds=uptime_seconds))  # Convert seconds to readable format
    await update.message.reply_text(f"⏳ **Bot Uptime:** `{uptime_str}`", parse_mode="Markdown")

# Video processing function
async def process_video(chat_id, video_url, context: CallbackContext):
    try:
        # Check if the video_url matches the VALID_URL_PATTERN
        if not re.match(VALID_URL_PATTERN, video_url):
            await context.bot.send_message(chat_id, "❌ Please send a valid **TeraBox or TeraShare video link**.")
            return
        
        # Notify user and get message ID
        processing_message = await context.bot.send_message(chat_id, "⏳ Processing your video link... Please wait. 🚀")

        # API request
        response = requests.post(API_URL, json={"video_url": video_url}, timeout=15)
        response.raise_for_status()  # Raises an error for non-200 status codes
        
        data = response.json()

        # Delete the processing message before sending the result
        await context.bot.delete_message(chat_id, processing_message.message_id)

        if "stream_link" in data:
            stream_link = data["stream_link"]

            # Create inline keyboard buttons
            buttons = [
                [InlineKeyboardButton("🎥 Watch Online", url=stream_link)],
                [InlineKeyboardButton("🤖 Developer", url=f"https://t.me/{owner}"),
                 InlineKeyboardButton("🌐 Channel", url=f"https://t.me/{channel}")]
                
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            # Send streaming link with buttons
            await context.bot.send_message(chat_id, "✅ Your streaming link is ready! Click below to watch 🎬", reply_markup=reply_markup)

        else:
            await context.bot.send_message(chat_id, f"❌ Error: {data.get('error', 'Failed to generate the stream link.')}")

    except requests.exceptions.Timeout:
        await context.bot.send_message(chat_id, "⚠️ The request timed out. Please try again later.")
    
    except requests.exceptions.RequestException as e:
        await context.bot.send_message(chat_id, f"⚠️ API Error: {str(e)}")
    
    except Exception as e:
        await context.bot.send_message(chat_id, f"⚠️ An unexpected error occurred: {str(e)}")




async def handle_message(update: Update, context: CallbackContext) -> None:
    # Ensure there is a message and it's a text message
    if not update.message or not update.message.text:
        return  # Handle the case where it's not a text message or there's no message
    
    message_text = update.message.text
    chat_id = update.message.chat_id
    
    chat_type = update.message.chat.type
        
    if chat_type not in ["private"]:
        await context.bot.send_message(
            update.message.chat_id,
            "🚫 I do not work in groups or channels. Please send me a message in Direct Message (DM).",
            parse_mode="Markdown"
        )
        return

    # Check if the message matches the valid URL pattern
    if re.match(VALID_URL_PATTERN, message_text):
        user = update.effective_user
        user_id = user.id
        username = user.username if user.username else "N/A"
        first_name = user.first_name if user.first_name else "N/A"

        # Prepare the user details message
        user_details = (
            f"📤 **User Information**:\n"
            f"🆔 **User ID**: `{user_id}`\n"
            f"👤 **Username**: @{username}\n"
            f"👤 **Name**: {first_name}\n\n"
        )

        # Prepare the message with the valid link
        message = f"\n------------------------------------------------\n✅ **TeraBox link received**:\n\n{user_details}\n{message_text}\n------------------------------------------------"
        await context.bot.send_message(chat_id=link_channel, text=message, parse_mode="Markdown")

        # Process the video link asynchronously
        asyncio.create_task(process_video(chat_id, message_text, context))
    
    else:
        # If the message is not a valid TeraBox link, send an error message
        await context.bot.send_message(chat_id, "❌ Please send a valid <b>TeraBox</b> or <b>TeraShare</b> video link. 🚀🎥", parse_mode="html")


async def send_user_ids(update: Update, context: CallbackContext) -> None:
    # Check if the user is an admin
    if update.message.from_user.id not in ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to view the user list. 🚫")
        return

    # Load user IDs
    user_ids = load_user_ids()
    total_users = len(user_ids)
    
    # Create a formatted list of user IDs with better code formatting
    user_list = "\n".join([f"{i + 1}) 🧑‍💻*User ID:* `{user_id}`" for i, user_id in enumerate(user_ids)])
    
    message = f"Total Users: {total_users} 🧑‍🤝‍🧑\n\n{user_list}"
    
    # Send the message
    await update.message.reply_text(message,parse_mode="MarkDown")



async def broadcast_message(update: Update, context: CallbackContext) -> None:
    # Check if the user is an admin
    if update.message.from_user.id not in ADMIN_USER_ID:
        await update.message.reply_text("❌ You are not authorized to broadcast messages.")
        return

    # Extract the message to broadcast (everything after /broad)
    message_to_broadcast = ' '.join(update.message.text.split()[1:]).strip()
    
    if not message_to_broadcast:
        await update.message.reply_text("❌ Please provide a message to broadcast.")
        return

    # Load user IDs
    user_ids = load_user_ids()
    success_count = 0
    fail_count = 0
    failed_users = []

    # Broadcast the message to each user
    for user_id in user_ids:
        try:
            await context.bot.send_message(user_id, message_to_broadcast)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failed_users.append(user_id)
            logger.error(f"Failed to send message to {user_id}: {e}")

    # Prepare the summary message
    summary_message = (
        f"🌐 Broadcast Summary of TeraBox bot:\n"
        f"❇️ Sent successfully to {success_count} users.\n"
        f"❌ Failed to send to {fail_count} users.\n"
        f"Blocked users or errors: {len(failed_users)}\n"
    )

    # Send the summary to the admin
    await update.message.reply_text(summary_message)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handler for /uptime
    application.add_handler(CommandHandler("uptime", send_uptime))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("users", send_user_ids))
    application.add_handler(CommandHandler("broad", broadcast_message))
    application.add_handler(CallbackQueryHandler(send_link_request, pattern="send_link"))

    display()
    application.run_polling()

if __name__ == '__main__':
    keep_alive()  # Starts the keep-alive function if needed
    
    while True:
        try:
            main()  # Call the main bot function here
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            time.sleep(5) 