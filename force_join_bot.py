import telebot
from telebot import types
import json
import os
from datetime import datetime

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"   # must contain :
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= COURSES DATA =================
COURSES = [
    {
        "name": "Video Editing",
        "link": "https://t.me/CouresbyAnkit"
    },
    {
        "name": "AI Editing",
        "link": "https://t.me/CouresbyAnkit"
    },
    {
        "name": "Documentary Editing",
        "link": "https://t.me/CouresbyAnkit"
    }
]

# ================= FORCE JOIN CHECK =================
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= DAILY SEARCH LOG =================
def log_search(user, text):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"stats_{today}.json"

    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump([], f)

    with open(filename, "r") as f:
        data = json.load(f)

    data.append({
        "user_id": user.id,
        "name": user.first_name,
        "username": user.username,
        "query": text,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    if is_member(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"🎉 *Welcome {message.from_user.first_name}!*\n\n"
            "✅ You now have full access.\n"
            "📚 Use /courses or search by typing."
        )
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ I Joined", callback_data="check_join")
        )

        bot.send_message(
            message.chat.id,
            "🔐 *Restricted Access*\n\n"
            "This bot is exclusive for our channel members.\n\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "After joining, press **I Joined** to unlock full access.",
            reply_markup=markup
        )

# ================= CHECK JOIN BUTTON =================
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        bot.edit_message_text(
            f"🎉 *Welcome {call.from_user.first_name}!*\n\n"
            "✅ You now have full access.\n"
            "📚 Use /courses or search by typing.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ You must join the channel first.\nThen press 'I Joined' again.",
            show_alert=True
        )

# ================= COURSES COMMAND =================
@bot.message_handler(commands=["courses"])
def courses(message):
    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"🔐 Join {CHANNEL_USERNAME} to access courses."
        )
        return

    text = "📚 *Available Courses*\n\n"
    for c in COURSES:
        text += f"🎓 {c['name']}\n"

    text += "\n🔍 *You can also search by typing course name*"

    bot.send_message(message.chat.id, text)

# ================= SEARCH HANDLER =================
@bot.message_handler(func=lambda m: not m.text.startswith("/") and m.text is not None)
def search_course(message):

    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"🔐 Join {CHANNEL_USERNAME} to search courses."
        )
        return

    query = message.text.lower()
    log_search(message.from_user, query)

    found = False

    for course in COURSES:
        if query in course["name"].lower():
            bot.send_message(
                message.chat.id,
                f"🎓 *{course['name']}*\n\n"
                f"📎 Access here:\n{course['link']}"
            )
            found = True

    if not found:
        bot.send_message(
            message.chat.id,
            f"😔 *Course Not Found*\n\n"
            f"🚧 `{message.text}` is not available right now.\n\n"
            f"✨ *Coming Soon!*\n"
            f"📩 DM 👉 @coursesbyankit\n"
            f"📢 Stay tuned 🔔"
        )

# ================= RUN BOT =================
print("🤖 Bot is running...")
bot.infinity_polling()
