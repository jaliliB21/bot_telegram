from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import instaloader


# Keeping users' status
user_states = {}


async def reels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 
    Requests a Reels video link from the user and updates their state.
    
    Sets the state to "waiting_for_reels_url" and displays a "Home" button for navigation.
    """

    chat_id = update.message.chat_id
    user_states[chat_id] = "waiting_for_reels_url"

    await update.message.reply_text(
        "📥 لطفا لینک ویدیو ریلز را ارسال کنید:", 
        reply_markup=ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)
    )


async def handle_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user input when a Reels link is sent. 

    Saves the link, updates the state, and prompts the user to choose a download option.
    """


    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_states and user_states[chat_id] == "waiting_for_reels_url":
        context.user_data["reels_url"] = text  
        user_states[chat_id] = "reels_options"

        keyboard = [
            [InlineKeyboardButton("📜 دانلود با کپشن", callback_data="reels_caption")],
            [InlineKeyboardButton("🖼️ دانلود با کاور", callback_data="reels_cover")],
            [InlineKeyboardButton("🎥 دانلود با کاور و کپشن", callback_data="reels_cover_caption")],
            [InlineKeyboardButton("📂 فقط ویدیو", callback_data="reels_only")]
        ]

        await update.message.reply_text(
            "📌 لطفا نوع دانلود را انتخاب کنید:", 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def download_reels(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """
    Processes the selected download option and retrieves the Reels video.

    Fetches the video, cover, or caption based on user choice and sends it to the chat.
    """

    print("download reel")
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_option = query.data
    reels_url = context.user_data.get("reels_url")

    if not reels_url:
        await query.answer("⛔ لینک نامعتبر. لطفا دوباره امتحان کنید.")
        return

    await query.message.edit_text("⏳ در حال پردازش ویدیو... لطفا صبر کنید.")

    try:
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, reels_url.split("/")[-2])
        video_url = post.video_url
        caption = post.caption
        cover_url = post.url

        if selected_option == "reels_caption":
            await context.bot.send_video(chat_id, video=video_url, caption=caption)
        elif selected_option == "reels_cover":
            await context.bot.send_photo(chat_id, photo=cover_url)
            await context.bot.send_video(chat_id, video=video_url)
        elif selected_option == "reels_cover_caption":
            await context.bot.send_photo(chat_id, photo=cover_url, caption=caption)
            await context.bot.send_video(chat_id, video=video_url)
        elif selected_option == "reels_only":
            await context.bot.send_video(chat_id, video=video_url)

        await query.message.edit_text("✅ ویدیو با موفقیت دانلود شد!")

    except Exception as e:
        await query.message.edit_text(f"⚠️ خطا در دانلود: {e}")

    if chat_id in user_states:
        del user_states[chat_id]
