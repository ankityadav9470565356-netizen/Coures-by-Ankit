import telebot
from telebot import types

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"   # must contain :
CHANNEL_USERNAME = "@CouresbyAnkit"       # your public channel
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= FUNCTION =================
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    if is_member(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"🎉 *Welcome {message.from_user.first_name}!*\n\n"
            "✅ You now have full access.\n"
            "📚 Use /courses to continue."
        )
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ I Joined", callback_data="check_join")
        )

        bot.send_message(
            message.chat.id,
            f"🔐 *Restricted Access*\n\n"
f"This bot is exclusive for our channel members.\n"
f"Please join the official channel to continue:\n"
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
            "📚 Use /courses to continue.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ You must join @CouresbyAnkit first.\nThen press 'I Joined' again.",
            show_alert=True
        )

# ================= COURSES COMMAND =================
@bot.message_handler(commands=["courses"])
def courses(message):
    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"❌ You must join {CHANNEL_USERNAME} to access courses."
        )
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 Video Editing", url="https://t.me/CouresbyAnkit"),
        types.InlineKeyboardButton("🤖 AI Editing", url="https://t.me/CouresbyAnkit"),
        types.InlineKeyboardButton("📺 Documentary Editing", url="https://t.me/CouresbyAnkit")
    )

    bot.send_message(
        message.chat.id,
        "📚 *Available Courses*",
        reply_markup=markup
    )

# ================= RUN BOT =================
print("🤖 Bot is running...")
bot.infinity_polling()
