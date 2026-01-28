import telebot
from telebot import types
import json, os, time
from datetime import datetime

# ================= CONFIG =================
API_TOKEN = "8561540975:AAELrKmHB4vcMe8Txnbp4F47jxqJhxfq3u8"
CHANNEL_USERNAME = "@CouresbyAnkit"
CHANNEL_LINK = "https://t.me/CouresbyAnkit"

ADMIN_IDS = [6003630443, 7197718325]
COURSES_FILE = "courses.json"

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# ================= ADMIN STATE =================
ADMIN_STATE = {}

# ================= DEFAULT COURSES =================
DEFAULT_COURSES = [
    {"name": "Edit To Earn – Video Editing", "link": "https://t.me/EditToEarnCoursesbyAnkit"},
    {"name": "Jeet Selal Fitness Course", "link": "https://arolinks.com/TrainingCoursebyJeetSelal"},
    {"name": "Go Viral – Kavya Karnatac", "link": "https://t.me/+d4Tto-Nc2hw2ODFl"},
    {"name": "Script & Storytelling – Saqlain Khan", "link": "https://arolinks.com/SaqlainkhanCourse"},
    {"name": "Instagram Growth – Detyo Bon", "link": "https://arolinks.com/DetyoBonInstagramCourse"},
    {"name": "ChatGPT Mastery – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "Time Management – Dhruv Rathee", "link": "https://arolinks.com/Vus4S"},
    {"name": "YouTube Automation – Ammar Nisar", "link": "https://arolinks.com/BiM5K"},
    {"name": "CapCut Mastery Course", "link": "https://t.me/CouresbyAnkit/447"},
    {"name": "Mr Beast Editor Course", "link": "https://t.me/AttractionDecodedManLifestyle/28"},
]

# ================= LOAD / SAVE =================
def load_courses():
    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "w") as f:
            json.dump(DEFAULT_COURSES, f, indent=2)
    with open(COURSES_FILE, "r") as f:
        return json.load(f)

def save_courses(data):
    with open(COURSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

COURSES = load_courses()

# ================= FORCE JOIN =================
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# ================= STATS =================
def log_search(user, query):
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    data = []
    if os.path.exists(file):
        data = json.load(open(file))
    data.append({
        "user": user.first_name,
        "username": user.username,
        "query": query,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    json.dump(data, open(file, "w"), indent=2)

def get_today_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    file = f"stats_{today}.json"
    if not os.path.exists(file):
        return 0, {}
    data = json.load(open(file))
    counter = {}
    for d in data:
        counter[d["query"]] = counter.get(d["query"], 0) + 1
    return len(data), counter

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ I Joined", callback_data="check_join")
        )
        bot.send_message(
            message.chat.id,
            "🔐 *Restricted Access*\n\nJoin our channel first 👇",
            reply_markup=kb
        )
        return

    bot.send_message(
        message.chat.id,
        f"🎉 *Welcome {message.from_user.first_name}!*\n\n📚 Use /courses or type to search 🔍"
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(c):
    if is_member(c.from_user.id):
        bot.edit_message_text(
            "✅ *Access Granted!*\n\n📚 Use /courses",
            c.message.chat.id,
            c.message.message_id
        )
    else:
        bot.answer_callback_query(c.id, "❌ Join channel first!", show_alert=True)

# ================= COURSES =================
@bot.message_handler(commands=["courses"])
def courses(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for c in COURSES:
        key = c["name"].lower().replace(" ", "_")
        kb.add(types.InlineKeyboardButton(f"🎓 {c['name']}", callback_data=f"course_{key}"))

    bot.send_message(
        message.chat.id,
        "📚 *Available Courses*\n\n👇 Select a course:",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("course_"))
def open_course(c):
    key = c.data.replace("course_", "")
    for course in COURSES:
        if key == course["name"].lower().replace(" ", "_"):
            bot.send_message(
                c.message.chat.id,
                f"🎉 *{course['name']}*\n\n🔗 {course['link']}"
            )
            bot.answer_callback_query(c.id)
            return
    bot.answer_callback_query(c.id, "❌ Course not found")

# ================= SEARCH =================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def search(m):
    if not is_member(m.from_user.id):
        return

    query = m.text.lower()
    log_search(m.from_user, query)

    msg = bot.send_message(m.chat.id, "🔍 Searching 🎬")
    for i in range(3):
        time.sleep(0.4)
        bot.edit_message_text(f"🔍 Searching 🎬{'.'*(i+1)}", m.chat.id, msg.message_id)

    for c in COURSES:
        if query in c["name"].lower():
            bot.edit_message_text(
                f"🎉 *Found!*\n\n🎓 {c['name']}\n🔗 {c['link']}",
                m.chat.id,
                msg.message_id
            )
            return

    bot.edit_message_text(
        "😔 *Course Not Available*\n\n🚧 Coming Soon!\n📩 DM 👉 @coursesbyankit",
        m.chat.id,
        msg.message_id
    )

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        return

    ADMIN_STATE[message.from_user.id] = None

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Add Course", "➖ Remove Course")
    kb.add("📊 View Stats", "❌ Exit Admin")

    bot.send_message(
        message.chat.id,
        "👮 *Admin Panel*",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text == "➕ Add Course" and m.from_user.id in ADMIN_IDS)
def admin_add(m):
    ADMIN_STATE[m.from_user.id] = "ADD"
    bot.send_message(m.chat.id, "Send:\n`Course Name | https://link`")

@bot.message_handler(func=lambda m: m.text == "➖ Remove Course" and m.from_user.id in ADMIN_IDS)
def admin_remove(m):
    ADMIN_STATE[m.from_user.id] = "REMOVE"
    text = "Send course name to remove:\n\n"
    for c in COURSES:
        text += f"• {c['name']}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📊 View Stats" and m.from_user.id in ADMIN_IDS)
def admin_stats(m):
    total, counter = get_today_stats()
    text = f"📊 *Today Stats*\n\n🔍 Searches: *{total}*\n"
    for k, v in counter.items():
        text += f"• `{k}` → {v}\n"
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def admin_text_handler(m):
    global COURSES

    state = ADMIN_STATE.get(m.from_user.id)

    if state == "ADD" and "|" in m.text:
        name, link = map(str.strip, m.text.split("|", 1))
        COURSES.append({"name": name, "link": link})
        save_courses(COURSES)
        ADMIN_STATE[m.from_user.id] = None
        bot.send_message(m.chat.id, f"✅ Added: *{name}*")
        return

    if state == "REMOVE":
        COURSES = [c for c in COURSES if c["name"].lower() != m.text.lower()]
        save_courses(COURSES)
        ADMIN_STATE[m.from_user.id] = None
        bot.send_message(m.chat.id, "🗑️ Course removed (if existed).")
        return

    if m.text == "❌ Exit Admin":
        ADMIN_STATE[m.from_user.id] = None
        bot.send_message(m.chat.id, "Exited admin panel", reply_markup=types.ReplyKeyboardRemove())

# ================= RUN =================
print("🤖 Bot is running...")
bot.infinity_polling()
