from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, \
                                        CallbackQueryHandler, filters, ContextTypes

from reels import reels_handler, handle_text, download_reels
from features import show_features


# main button 
main_buttons = ReplyKeyboardMarkup(
    [["📥 دانلود ریلز", "📌 امکانات دیگر"]],
    resize_keyboard=True
)


async def home_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.delete()  
    except:
        pass  

    await update.message.reply_text(
        "به منوی اصلی بازگشتید", 
        reply_markup=main_buttons
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """send welcome message and show main button"""
    await update.message.reply_text(
        "🎉 خوش آمدید! لطفا یک گزینه را انتخاب کنید:",
        reply_markup=main_buttons
    )


async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ورودی‌ها"""
    text = update.message.text
    # chat_id = update.message.chat_id

    if text == "📥 دانلود ریلز":
        await reels_handler(update, context)
        context.user_data["waiting_for_reels_url"] = True  

    elif text == "📌 امکانات دیگر":
        await show_features(update, context)

    elif context.user_data.get("waiting_for_reels_url", False):  
        await handle_text(update, context)
        context.user_data["waiting_for_reels_url"] = False  
        

def main():
    """this function run bot and handele functions"""
    app = Application.builder().token("7374641101:AAHKdik0DRXVtm-lzm3Vi_fTg_uvBcooV9Y").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("🏠"), home_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handler))


    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(download_reels))


    app.run_polling()


if __name__ == "__main__":
    main()
