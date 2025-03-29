from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import instaloader

import os
import shutil


# Keeping users' status
user_states = {}


async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 
    Requests a Post video or image link from the user and updates their state.
    
    Sets the state to "waiting_for_post_url" and displays a "Home" button for navigation.
    """

    chat_id = update.message.chat_id
    user_states[chat_id] = "waiting_for_post_url"

    await update.message.reply_text(
        "📥 لطفا لینک پست را ارسال کنید:", 
        reply_markup=ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)
    )


async def handle_btn_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user input when a Reels link is sent. 

    Saves the link, updates the state, and prompts the user to choose a download option.
    """


    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_states and user_states[chat_id] == "waiting_for_post_url":
        context.user_data["post_url"] = text  
        user_states[chat_id] = "post_options"

        keyboard = [
            [InlineKeyboardButton("📜 دانلود با کپشن", callback_data="post_caption")],
            [InlineKeyboardButton("دانلود بدون کپشن", callback_data="post_only")],
           
        ]

        await update.message.reply_text(
            "📌 لطفا نوع دانلود را انتخاب کنید:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    
async def post_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function downloads the associated media (images or videos),
    and sends them to the user's Telegram chat.

    Parameters:
    - update: The incoming update from Telegram.
    - context: The context containing user data and bot information.
    """

    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    choice = query.data

    if chat_id in user_states and user_states[chat_id] == "post_options":
        post_url = context.user_data.get("post_url")
        if not post_url:
            await query.edit_message_text("❌ لینک پست یافت نشد. لطفاً دوباره تلاش کنید.")
            return

        loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            save_metadata=False,
            post_metadata_txt_pattern=""
        )

        try:
            shortcode = post_url.split("/")[-2]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            caption = post.caption if choice == "post_caption" else ""
            target_dir = f"{chat_id}_post"
            loader.download_post(post, target=target_dir)

            media_files = [f for f in os.listdir(target_dir) if f.endswith(('.jpg', '.mp4'))]

            for media_file in media_files:
                media_path = os.path.join(target_dir, media_file)
                with open(media_path, 'rb') as file:
                    if media_file.endswith('.jpg'):
                        await context.bot.send_photo(chat_id=chat_id, photo=file, caption=caption[:1024])
                    elif media_file.endswith('.mp4'):
                        await context.bot.send_video(chat_id=chat_id, video=file, caption=caption[:1024])
                os.remove(media_path)

            shutil.rmtree(target_dir)
            await query.edit_message_text("✅ دانلود و ارسال پست با موفقیت انجام شد.")
        except Exception as e:
            await query.edit_message_text(f"❌ خطا در دانلود پست: {str(e)}")

        user_states[chat_id] = None
