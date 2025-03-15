from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes


home_button = ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)


async def show_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
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
