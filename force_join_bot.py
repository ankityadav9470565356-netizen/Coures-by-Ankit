import telebot
from telebot import types
import json
import os
import time
from datetime import datetime

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]  # 👈 Put your Telegram ID
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= LOAD / SAVE COURSES =================
def load_courses():
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "w") as f:
            json.dump([], f)
    with open(COURSES_FILE, "r") as f:
        return json.load(f)

def save_courses(data):
    with open(COURSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

COURSES = load_courses()

# ====== Add a test course if list is empty ======
if not COURSES:
    COURSES.append({
        "name": "Python Basics",
        "link": "https://t.me/test"
    })
    save_courses(COURSES)

# ================= FORCE JOIN CHECK =================
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= LOG SEARCH =================
def log_search(user, text):
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    data = []
    if os.path.exists(file):
        with open(file, "r") as f:
            data = json.load(f)
    data.append({
        "user": user.first_name,
        "username": user.username,
        "query": text,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ I Joined", callback_data="check_join")
        )
        bot.send_message(
            message.chat.id,
            "🔐 *Restricted Access*\n\nJoin our channel to use this bot 👇",
            reply_markup=markup
        )
        return

    bot.send_message(
        message.chat.id,
        f"🎉 *Welcome {message.from_user.first_name}!*\n\n"
        "📚 Use /courses or type a search query"
    )

# ================= CHECK JOIN CALLBACK =================
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        bot.edit_message_text(
            "✅ *Access Granted!*\n\n📚 Use /courses",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Join channel first!", show_alert=True)

# ================= COURSES INLINE =================
@bot.message_handler(commands=["courses"])
def show_courses(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, f"🔐 Join {CHANNEL_USERNAME} to access courses.")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for course in COURSES:
        callback_data = f"course_{course['name'].lower().replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton(f"🎓 {course['name']}", callback_data=callback_data))

    bot.send_message(
        message.chat.id,
        "📚 *Available Courses*\n\n👇 Select a course:",
        reply_markup=markup
    )

# ================= COURSE BUTTON CALLBACK =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def course_selected(call):
    course_key = call.data.replace("course_", "")
    for course in COURSES:
        if course_key == course["name"].lower().replace(" ", "_"):
            bot.send_message(
                call.message.chat.id,
                f"🎓 *{course['name']}*\n\n📎 Access here:\n{course['link']}"
            )
            bot.answer_callback_query(call.id)
            return
    bot.answer_callback_query(call.id, "❌ Course not found")

# ================= SEARCH =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def search(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, f"🔐 Join {CHANNEL_USERNAME} to search courses.")
        return

    query = message.text.lower()
    log_search(message.from_user, query)

    msg = bot.send_message(message.chat.id, "🔍 Searching 🎬")
    for i in range(3):
        time.sleep(0.5)
        bot.edit_message_text(f"🔍 Searching 🎬{'.' * (i+1)}", message.chat.id, msg.message_id)

    for course in COURSES:
        if query in course["name"].lower():
            bot.edit_message_text(
                f"🎉 *Found!*\n\n🎓 {course['name']}\n📎 {course['link']}",
                message.chat.id,
                msg.message_id
            )
            return

    bot.edit_message_text(
        "😔 *Not Available*\n\n🚧 This course is coming soon!\n📩 DM 👉 @coursesbyankit",
        message.chat.id,
        msg.message_id
    )

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Add Course", "➖ Remove Course")
    markup.add("❌ Exit Admin")
    bot.send_message(message.chat.id, "👮 *Admin Panel*", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "➕ Add Course")
def add_course(message):
    bot.send_message(message.chat.id, "Send:\n`Course Name | Link`")

@bot.message_handler(func=lambda m: "|" in m.text and m.from_user.id in ADMIN_IDS)
def save_course(message):
    name, link = map(str.strip, message.text.split("|"))
    COURSES.append({"name": name, "link": link})
    save_courses(COURSES)
    bot.send_message(message.chat.id, "✅ Course added!")

@bot.message_handler(func=lambda m: m.text == "➖ Remove Course")
def remove_course(message):
    text = "Send course name to remove:\n"
    for c in COURSES:
        text += f"• {c['name']}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and m.from_user.id in ADMIN_IDS)
def delete_course(message):
    global COURSES
    COURSES = [c for c in COURSES if c["name"].lower() != message.text.lower()]
    save_courses(COURSES)
    bot.send_message(message.chat.id, "🗑️ Course removed (if existed).")

# ================= RUN BOT =================
print("🤖 Bot running...")
bot.infinity_polling()
