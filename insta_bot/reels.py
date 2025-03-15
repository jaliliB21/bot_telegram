from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import instaloader

# نگه داشتن وضعیت کاربران
user_states = {}

async def reels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست لینک و نمایش دکمه خانه"""
    print("reels handeler")
    chat_id = update.message.chat_id
    user_states[chat_id] = "waiting_for_reels_url"

    await update.message.reply_text(
        "📥 لطفا لینک ویدیو ریلز را ارسال کنید:", 
        reply_markup=ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handeler text")

    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_states and user_states[chat_id] == "waiting_for_reels_url":
        context.user_data["reels_url"] = text  # ذخیره لینک ریلز
        user_states[chat_id] = "reels_options"  # تغییر وضعیت

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
    print("reel download")

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