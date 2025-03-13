from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot import start, reels_handler, story_handler, home_handler, handle_text, download_reels, handle_story_download

TOKEN = "8110195579:AAEcOSgj6lSzJkJM0STGFQYFSVpYbKDU2pQ"


def main():
    """run telegram bot"""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("📹 دانلود ریلز"), reels_handler))
    app.add_handler(MessageHandler(filters.Text("📸 دانلود استوری"), story_handler))
    app.add_handler(MessageHandler(filters.Text("🏠 هوم"), home_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(download_reels))

    app.run_polling()


if __name__ == "__main__":
    main()
