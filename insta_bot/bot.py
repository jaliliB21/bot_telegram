import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import instaloader

# Initialize Instaloader
L = instaloader.Instaloader()

# Dictionary to store user states
user_states = {}

# Main buttons next to the typing bar
main_buttons = ReplyKeyboardMarkup([["📹 دانلود ریلز", "📸 دانلود استوری"]], resize_keyboard=True)

# Home button for returning to the main menu
home_button = ReplyKeyboardMarkup([["🏠 خانه"]], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and displays main buttons."""
    await update.message.reply_text(
        "🎉 خوش آمدید! لطفا یک گزینه را انتخاب کنید:",
        reply_markup=main_buttons
    )


async def reels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user for a Reels URL when they click the download button."""
    await update.message.reply_text("📥 لطفا لینک ویدیو ریلز را ارسال کنید:", reply_markup=home_button)
    user_states[update.message.chat_id] = "waiting_for_reels_url"


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles receiving the URL and displaying download options."""
    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_states and user_states[chat_id] == "waiting_for_reels_url":
        context.user_data["reels_url"] = text

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

        user_states[chat_id] = "reels_options"


async def download_reels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles downloading Reels based on the selected option."""
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_option = query.data
    reels_url = context.user_data.get("reels_url", None)

    if not reels_url:
        await query.answer("⛔ لینک نامعتبر. لطفا دوباره امتحان کنید.")
        return

    await query.message.edit_text("⏳ در حال پردازش ویدیو... لطفا صبر کنید.")

    try:
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


async def home_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns to the main menu and displays the initial buttons."""
    await update.message.reply_text("🏠 بازگشت به منوی اصلی", reply_markup=main_buttons)

    if update.message.chat_id in user_states:
        del user_states[update.message.chat_id]


async def story_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles downloading a story - only requests a link."""
    await update.message.reply_text("📥 لطفا لینک استوری را ارسال کنید:", reply_markup=home_button)
    user_states[update.message.chat_id] = "waiting_for_story_url"


async def handle_story_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles story download based on the received link."""
    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_states and user_states[chat_id] == "waiting_for_story_url":
        await update.message.reply_text("⏳ در حال پردازش استوری...")

        try:
            post = instaloader.Post.from_shortcode(L.context, text.split("/")[-2])
            video_url = post.video_url

            await context.bot.send_video(chat_id, video=video_url)
            await update.message.reply_text("✅ استوری با موفقیت دانلود شد!")
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطا در دانلود استوری: {e}")

        del user_states[chat_id]
