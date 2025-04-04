from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, \
                                        CallbackQueryHandler, filters, ContextTypes

from reels import reels_handler, handle_btn, download_reels
from post import post_handler, handle_btn_post, post_download
from features import show_features
from comments import show_featuers as sf
from comments import process_post_link, request_link


# main button 
main_buttons = ReplyKeyboardMarkup(
    [
        ["📥 دانلود ریلز", "📌 امکانات دیگر"],
        ["دانلود پست", "دانلود کامنت"]
    ],
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
    """
    Handles user input and triggers corresponding actions based on the message text.
    """

    text = update.message.text

    if text == "📥 دانلود ریلز":
        await reels_handler(update, context)
        context.user_data["waiting_for_reels_url"] = True  

    elif text == "📌 امکانات دیگر":
        await show_features(update, context)
    
    elif text == "دانلود پست":
        await post_handler(update, context)
        context.user_data["waiting_for_post_url"] = True 

    elif text == "دانلود کامنت":
        await sf(update)
    

    elif context.user_data.get("waiting_for_reels_url", False):  
        await handle_btn(update, context)
        context.user_data["waiting_for_reels_url"] = False 

    elif context.user_data.get("waiting_for_post_url", False):  
        await handle_btn_post(update, context)
        context.user_data["waiting_for_post_url"] = False   

    elif context.user_data.get("waiting_for_link_comment", False):
        await process_post_link(update, context)

    
    # elif context.user_data.get("waiting_for_story", False):  
    #     print("yes")
    #     await download_and_send_story(update, context)
    
    # elif context.user_data.get("waiting_for_profile", False):  
        
    #     await download_and_send_profile(update, context)
        
    
    
    
async def feature_handler(update: Update):
    query = update.callback_query
    query.answer()

    # if query.data == "download_story":
    #     await request_story_link(update, context)
    
    # if query.data == "download_profile":
    #     await request_profile_link


async def feature_handler_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    if query.data == "download_comment":
        await request_link(update, context)


def main():
    """this function run bot and handele functions"""
    app = Application.builder().token("7775427064:AAECpqHDGMxHPG1pb5ih-KhctptdBhUhFuM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("🏠"), home_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handler))

    # reel handeler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_btn))
    app.add_handler(CallbackQueryHandler(download_reels, pattern="^reels_"))

    # post handeler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_btn_post))
    app.add_handler(CallbackQueryHandler(post_download, pattern="^post_"))

    # comment handeler
    app.add_handler(CallbackQueryHandler(request_link, pattern="^download_comment$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, feature_handler_comment))
    app.add_handler(CallbackQueryHandler(process_post_link))


    # story handeler
    # app.add_handler(CallbackQueryHandler(request_story_link, pattern="^download_story$"))

    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, feature_handler))
    # app.add_handler(CallbackQueryHandler(download_and_send_story))

    # app.add_handler(CallbackQueryHandler(request_profile_link, pattern="^download_profile$"))
    # app.add_handler(CallbackQueryHandler(download_and_send_profile))


    print("runned")


    try:
        app.run_polling()
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    main()
