from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

import instaloader
import os


home_button = ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)


L = instaloader.Instaloader()

# USERNAME = ""
# PASSWORD = ""

# session_file = f"{USERNAME}.session"

# if os.path.exists(session_file):
#     L.load_session_from_file(USERNAME, session_file)
# else:
#     L.login(USERNAME, PASSWORD)
#     L.save_session_to_file(session_file)


async def show_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends feature options with inline buttons and prompts the user to select one.
    """

    if update.message:  
        keyboard = [
            [InlineKeyboardButton("📸 دانلود استوری", callback_data="download_story")],
            [InlineKeyboardButton("🔍 دانلود بیو", callback_data="download_bio")],
            [InlineKeyboardButton("🖼️ دانلود عکس پروفایل", callback_data="download_profile")],
        ]

        try:
            await update.message.reply_text(
                "⚙️",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            await update.message.reply_text(
                "لطفا یکی از خدمات فوق را انتخاب نمایید",  
                reply_markup=home_button
            )

                     
        except Exception as e:
            print(f"Error: {e}")


async def request_story_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """request give story link"""
    chat_id = update.effective_chat.id
    context.user_data["waiting_for_story"] = True  

    await update.effective_message.reply_text("🔗 لطفاً لینک استوری را ارسال کنید:")
    

async def download_and_send_story(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("waiting_for_story"):
        return

    chat_id = update.message.chat_id
    story_url = update.message.text.strip()
    
    await update.message.reply_text("⏳ در حال پردازش... لطفاً صبر کنید.")

    username = story_url.split("/")[-3]  

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        found_story = False
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                found_story = True
                file_path = f"{username}_story.mp4" if item.video_url else f"{username}_story.jpg"
                L.download_storyitem(item, username)

                if item.video_url:
                    with open(file_path, "rb") as video:
                        await context.bot.send_video(chat_id, video=video)
                else:
                    with open(file_path, "rb") as photo:
                        await context.bot.send_photo(chat_id, photo=photo)

                os.remove(file_path)
                break  

        if not found_story:
            await update.message.reply_text("❌ استوری‌ای برای این کاربر پیدا نشد.")

        context.user_data["waiting_for_story"] = False  

    except Exception as e:
        await update.message.reply_text(f"⛔ خطا در دانلود استوری: {e}")
        context.user_data["waiting_for_story"] = False
    