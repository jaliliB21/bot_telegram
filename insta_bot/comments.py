from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import instaloader

import os
import json

# Keeping users' status
user_states = {}


home_button = ReplyKeyboardMarkup([["🏠"]], resize_keyboard=True)


def get_instaloader_instance(username, password):
    """
    Create and return an instance of Instaloader using a saved session.
    If the session does not exist, log into the account and save the session.
    """
    print("login")
    L = instaloader.Instaloader()
    session_file = f"{username}.session"

    try:
        if os.path.exists(session_file):
            L.load_session_from_file(username)
        else:
            L.login(username, password)
            L.save_session_to_file()
    except instaloader.exceptions.InstaloaderException as e:
        print(f"خطا در مدیریت نشست: {e}")

    return L


async def show_featuers(update: Update):

    if update.message:  
        keyboard = [
            [InlineKeyboardButton("دانلود کامنت", callback_data="download_comment")],
            [InlineKeyboardButton("قرعه کشی", callback_data="lottery")],
            
        ]

        try:
            await update.message.reply_text(
                "⚙️⚙️",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            await update.message.reply_text(
                "لطفا یکی از خدمات فوق را انتخاب نمایید",  
                reply_markup=home_button
            )

                     
        except Exception as e:
            print(f"Error: {e}")


async def request_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    context.user_data["waiting_for_link_comment"] = True  
    await update.effective_message.reply_text("لطفاً لینک پست اینستاگرام را ارسال کنید:")


async def process_post_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    It processes the Instagram post link, downloads the comments and sends them as a JSON file.
    """

    chat_id = update.message.chat_id
    post_url = update.message.text

    # Extract the post ID from the link
    try:
        shortcode = post_url.split("/")[-2]
    except IndexError:
        await context.bot.send_message(chat_id=chat_id, text="لینک نامعتبر است. لطفاً یک لینک معتبر ارسال کنید.")
        return

    
    loader = get_instaloader_instance("python.org1", "M14H$+20j1")
    
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        comments = []

        for comment in post.get_comments():
            comments.append({
                'id': comment.id,
                'created_at_utc': comment.created_at_utc.isoformat(),
                'text': comment.text,
                'owner': {
                    'username': comment.owner.username,
                    'full_name': comment.owner.full_name,
                    'id': comment.owner.userid,
                },
            })

        # save comments in a json file
        comments_file = f"{shortcode}_comments.json"
        with open(comments_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)

        # send file for user
        with open(comments_file, 'rb') as f:
            await context.bot.send_document(chat_id=chat_id, document=f)

        # remove the file from the server
        os.remove(comments_file)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"خطا در دانلود کامنت‌ها: {str(e)}")